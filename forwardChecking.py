import copy

class forwardChecking:

    def __init__(self, n):
        # number of queens
        self.n = n
        # array of boolean for if a value has been assigned
        self.assigned = []
        for i in range(n):
            self.assigned.append(False)
        # The domains 2d array of n x n
        self.domains = []
        for i in range(n):
            row = []
            for j in range(n):
                row.append(j)
            self.domains.append(row)
        # Stack for var before it is assigned
        self.beforeAssign = []
        # Stack for checkpoints
        self.checkpoint = []
        # Array for the constraints
        self.cons = []
        self.setupCons()

    def setupCons(self):
        """
            Creates the constraints table for n queens in extension
            constraints table is [i, j, xi, xj]
            values in the table are the accepted values
        """
        for i in range(self.n):
            for j in range(self.n):
                if i == j:
                    continue
                for xi in range(self.n):
                    for xj in range(self.n):
                        if xj != xi:
                            if xj != xi + (j-i) and xj != xi - (j-i):
                                self.cons.append([i, j, xi, xj])
        print(self.cons)

    def isComplete(self):
        """
            Check if all vars have been assigned using the assigned array
        """
        for var in self.assigned:
            if not var:
                return False
        return True

    def display(self):
        """
            Displays the current values in the domains
        """
        for i in range(6):
            print("x", i, ": ", self.domains[i])

    def storeCheckpoint(self):
        """
            stores the value of domains before it is pruned
            uses deepcopy to make a copy without affecting the original array
        """
        self.checkpoint.append(copy.deepcopy(self.domains))

    #
    def assign(self, var, val):
        """
            assigns the value in the domain at row var to val
            :param var : int - points to the row in the domain:
            :param val : int - is the value to assign:
        """
        self.assigned[var] = True
        # Making a copy of the domain[var] so that it can be restored on unassign
        self.beforeAssign.append(copy.deepcopy(self.domains[var]))
        self.domains[var] = [val]

    def unassign(self, var):
        """
            unassigns the domain at var and restores it top what it was before assigning
            :param var : int - points to the row in the domain:
            :param val : int - is the value to unassign:
        """
        self.assigned[var] = False
        self.domains[var] = self.beforeAssign.pop()

    def deleteValue(self, var, val):
        """
            deletes the value from the domain at row var
            :param var : int - points to the row in the domain::
            :param val : int - value to remove from the domain:
        """
        self.domains[var].remove(val)

    def restoreValue(self, var, val):
        """
            restores the value in the domain at row var
            :param var : int - points to the row in the domain::
            :param val : int - value to add to the domain:
        """
        self.domains[var].append(val)

    def forwardChecking(self, varList):
        """
             Main function for forward checking
            :param varList : array - List of the rows that have not been assigned by a left branch
        """
        # Check if a solution has been found and if True display the result
        if self.isComplete():
            print("Complete: ")
            self.display()
            exit()
        # Select the var and val
        var = varList[0]
        val = self.domains[var][0]
        self.branchFCLeft(varList, var, val)
        self.branchFCRight(varList, var, val)

    def branchFCLeft(self, varList, var, val):
        """
            The left branch of 2-way forward checking
            Values are only assigned in this branch
            :param varList : array - List of rows that have not been assigned
            :param var : int - points to the row in the domain::
            :param val : int - value from the domain:
        """
        print(" Left branch x:", var, " = ", val)
        self.assign(var, val)
        if self.reviseFutureArcs(varList, var):
            # To get varList - var in forward check but keep varList correct in this function make a copy
            varListCopy = copy.deepcopy(varList)
            # Remove the var from the copy of var list
            # Then varList stays correct in the case of backtracking later
            varListCopy.remove(var)
            print("Revised domains:")
            self.display()
            self.forwardChecking(varListCopy)
        print(" Undoing Left branch x:", var, " = ", val)
        self.undoPruning()
        self.unassign(var)
        self.display()

    def branchFCRight(self, varList, var, val):
        """
            The right branch of 2-way forward checking
            Values cannot be assigned here
            :param varList : array - List of rows that have not been assigned
            :param var : int - points to the row in the domain::
            :param val : int - value from the domain:
        """
        print(" Right branch x:", var, " != ", val)
        self.deleteValue(var, val)
        if self.domains[var] != []:
            if self.reviseFutureArcs(varList, var):
                print("Revised domains: ")
                self.display()
                self.forwardChecking(varList)
            print("undoing Right branch x:", var, " != ", val)
            self.undoPruning()
            self.display()
        self.restoreValue(var, val)
        self.display()

    def reviseFutureArcs(self, varList, var):
        """
            revise future arcs checks each arc of var to a var that has not been assigned
            calls the revise method
            :param varList : array - List of rows that have not been assigned
            :param var : int - points to the row in the domain::
        """
        # Store the values of the domain in case of backtracking
        self.storeCheckpoint()
        # Loop through each var thats not been assigned
        for i in range(len(varList)):
            futureVar = varList[i]
            if futureVar == var:
                continue
            else:
                consistent = self.revise(futureVar, var)
                if not consistent:
                    print("DOMAIN EMPTIED X: ", futureVar)
                    return False
        return True

    def revise(self, futureVar, var):
        """
            Revise prunes the values in futureVar that do not fit the constraints
            :param var : int - points to the row in the domain::
            :param futureVar : int - points to a row in the domain that has not yet been assigned:
        """
        futureDomain = self.domains[futureVar]
        # if its a right branch there should be no pruning as its not making any assignment
        if len(self.domains[var]) > 1:
            return True
        value = self.domains[var][0]
        i = 0
        # Using a while loop to check values as the length of future domain will change as values are pruned
        while i < len(
                futureDomain) and futureDomain != []:
            # If the values are not in the constraint store
            if [var, futureVar, self.domains[futureVar][i], value] not in self.cons:
                # If the domain row can no longer be emptied
                if len(self.domains[futureVar]) <= 1:
                    # Arc is not consistent
                    return False
                # else prune the value
                self.deleteValue(futureVar, futureDomain[i])
            else:
                i = i + 1
        return True

    def undoPruning(self):
        """
            Undos the last bit of pruning
            Restores the values of the domains
        """
        self.domains = self.checkpoint.pop() # Pop most recent checkpoint off the stack


# N is the number of queens so in this case 6-Queens
n = 6
# Setup var list separately as it is not a global variable
varList = []
for i in range(n):
    varList.append(i)

# Create the 6-queens instance
fc = forwardChecking(n)
# Call the forward checking method
fc.forwardChecking(varList)
