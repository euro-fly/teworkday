# NOTE: As I am writing this in Python, there are some language-specific things I should mention.
# 1. This is Python 2.7, not Python 3.
# 2. I would normally have one extra class here (and on the UML diagram), but Python makes you jump
# through hoops to implement the singleton pattern. I've opted instead to represent what this class
# would have done as global functions and a global variable.

class User:
    def __init__(self, userid, skillsKnown = [], skillsLearning = []):
        self.id = userid # all three fields are specified by the user at account creation
        self.skillsKnown = set()
        self.skillsLearning = set()
        for skill in skillsKnown:
            self.addSkillToKnown(skill)
        for skill in skillsLearning:
            self.addSkillToLearning(skill)
    def getId(self):
        return self.id
    def addSkillToKnown(self, skill):
        if skill in self.skillsKnown:
            print "Skill already possessed." # this will be a popup or notification in the full app
        elif skill in self.skillsLearning:
            self.skillsLearning.remove(skill)
            self.skillsKnown.add(skill)
            #print "Learned a new skill."
        else:
            self.skillsKnown.add(skill)
            #print "Learned a new skill."
    def addSkillToLearning(self, skill):
        if skill in self.skillsKnown:
            print "Skill already possessed." # this will be a popup or notification in the full app
        else:
            self.skillsLearning.add(skill)
            #print "Now learning a new skill."
    def knowsSkill(self, skill):
        return skill in self.skillsKnown
    def isLearningSkill(self, skill):
        return skill in self.skillsLearning
    def createProject(self, name, requiredSkills):
        project = Project(name, requiredSkills, self)
        projectsList[name] = project
    def getSkillsKnown(self):
        return self.skillsKnown
    def getSkillsLearning(self):
        return self.skillsLearning
    def getRecommendedProjects(self):
        return recommendProjectsForUser(self)
    def requestToJoinProject(self, project):
        project.receiveUserRequest(self)
    def processFeedback(self, feedback):
        ## arbitrarily going to say the user needs a feedback rating of > 50 to be considered having learned the skills.
        ## naturally, this will change depending on what the specification actually is, but for now... > 50.
        if feedback.getRating() > 50:
            for skill in feedback.getTargetSkills():
                if self.isLearningSkill(skill):
                    self.addSkillToKnown(skill)
                    print "As project owner feedback was satisfactory, user " + self.id + " has learned a new skill."
                # The assumption is that the project owner wouldn't make them use skills they're not interested in.

class Skill:
    def __init__(self, name):
        self.name = name
    def getName(self):
        return self.name

class Project:
    def __init__(self, name, skills, owner):
        self.name = name
        self.requiredSkills = set(skills)
        self.owner = owner
        self.members = set()
        self.pendingMembers = set() # we use sets here because no duplicates.
        self.completed = False # we can't create an already-completed project...
    def getName(self):
        return self.name
    def getRequiredSkills(self):
        return self.requiredSkills
    def getCompleted(self):
        return self.completed
    def getOwner(self):
        return self.owner
    def isOwner(self):
        return current_user == self.owner
    def getCompatibility(self, user):
        if self.isOwner():
            userSkills = user.getSkillsKnown().union(user.getSkillsLearning())
            return len(list(userSkills & self.requiredSkills))
        else:
            print "Access denied. Current user is not the owner."
    def getPendingUsers(self):
        if self.isOwner():
            return self.pendingMembers
        else:
            print "Access denied. Current user is not the owner."
    def receiveUserRequest(self, user):
        if user in self.members:
            print "User is already in the project members list."
        else:
            self.pendingMembers.add(user)
            print "User added to pending members..."
    def approveUserRequest(self, user):
        if self.isOwner():
            if user not in self.pendingMembers:
                print "Can't handle a request from a non-pending user."
            else:
                self.pendingMembers.remove(user)
                self.members.add(user)
                print "Added a member to the project."
        else:
            print "Access denied. Current user is not the owner."
    def denyUserRequest(self, user):
        if self.isOwner():
            if user not in self.pendingMembers:
                print "Can't handle a request from a non-pending user."
            else:
                self.pendingMembers.remove(user)
        else:
            print "Access denied. Current user is not the owner."
    def completeProject(self):
        if self.isOwner():
            self.completed = True
            for member in self.members:
                print "Please rate " + member.getId()
                rating = None
                while True:
                    try:
                        rating = int(raw_input())
                    except ValueError:
                        print "Invalid number."
                        continue
                    else:
                        break
                self.sendFeedback(member, rating)
            print "Project " + self.getName() + " is complete."
        else:
            print "Access denied. Current user is not the owner."
    def sendFeedback(self, user, rating):
        feedback = Feedback(self.requiredSkills, rating)
        user.processFeedback(feedback)
            
class Feedback:
    def __init__(self, targetSkills, rating):
        self.targetSkills = targetSkills
        self.rating = rating
    def getTargetSkills(self):
        return self.targetSkills
    def getRating(self):
        return self.rating

projectsList = dict() # project name -> project instance

def addProject(project):
    projectsList[project.getName()] = project

def getProjectByName(name):
    return projectsList[name]
    
def recommendProjectsForUser(user):
    # for the purposes of simplicity, this returns only one project at most, and can be expanded to support returning the top X projects.
    if len(projectsList) < 1:
        return [] #if there are no projects, return an empty list.
    elif len(projectsList) == 1:
        if projectsList[key].getCompleted() == False and projectsList[key].getOwner() != user:
            return [projectsList.keys()[0]] # if there is only one item, and it's not already completed, and the user didn't create it...
        else:
            return []
    else:
        # We get the total compatibility by checking the intersection of the user's
        # learned + in-progress skills and the project's required skills.
        # We COULD weigh them differently, but since the specification didn't list
        # whether to prioritize their skills or interests, we'll weigh them equally.
        userSkills = user.getSkillsKnown().union(user.getSkillsLearning())
        mostCompatible = projectsList.keys()[0]
        compatibilityRating = len(list(userSkills & projectsList[mostCompatible].getRequiredSkills()))
        for key in projectsList.keys():
            if projectsList[key].getCompleted() == False and projectsList[key].getOwner() != user:
                newCompatibilityRating = len(list(userSkills & projectsList[key].getRequiredSkills()))
                if newCompatibilityRating > compatibilityRating:
                    mostCompatible = key
                    compatibilityRating = newCompatibilityRating
        print mostCompatible + " is the recommended project for you."
        return [projectsList[mostCompatible]]
    
# uncomment the following block for some user tests...

##skill_one = Skill("C Programming")
##skill_two = Skill("UML Diagram Design")
##skill_three = Skill("Underwater Basket Weaving")
##
##other_user = User("Jeff Jones", [skill_one, skill_two], [skill_three])
##
##my_user = User("John Smith", [skill_one], [skill_two])
##
##current_user = my_user # I've implemented (INCREDIBLY BASIC) "authentication". Think of current_user as the logged-in user.
##
##print current_user.getRecommendedProjects() # should print an empty list, since there are no projects. 
##current_user.createProject("PR1", [skill_three]) # create a project with one desired skill...
##current_user.createProject("PR2", [skill_three, skill_two, skill_one]) # create a project with all three desired skills...
##proj_one = getProjectByName("PR1")
##proj_two = getProjectByName("PR2")
##current_user = other_user # switch users
##recommendedProject = current_user.getRecommendedProjects()[0] # check which one is recommended. Should be PR2.
##current_user.requestToJoinProject(recommendedProject) 
##proj_two.getPendingUsers() # should fail out. only project owner can see the requests.
##current_user = my_user # switch back to our creator user
##print proj_two.getPendingUsers() # now that we're back as the original user, let's check our requests...
##proj_two.denyUserRequest(other_user) # denial should work.
##proj_two.approveUserRequest(other_user) # approval should NOT work because we denied Jeff's request, and so he is not in the pending queue...
##current_user = other_user # switch users
##current_user.requestToJoinProject(recommendedProject) # request this again
##current_user = my_user # switch back to our creator user again
##print proj_two.getCompatibility(other_user) # check the other user's compatibility
##proj_two.approveUserRequest(other_user) # since we're satisfied with Jeff's capabilities, we can approve his request
##proj_two.completeProject() # should prompt us to rate Jeff on stdout.
##current_user = other_user
##recommendedProject = current_user.getRecommendedProjects()[0] # check which one is recommended. Should be PR1, now that PR2 is marked done.
