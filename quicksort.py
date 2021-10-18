def sort(array=None):
    """
    A function used to sort an array by using the quicksort algorithm.
    """

    if array is None:
        array = [9.3, 10.0, 2.3, ]

    less = []
    equal = []
    greater = []

    if len(array) > 1:
        pivot = array[0]

        for x in array:
            if x < pivot:
                less.append(x)
            elif x == pivot:
                equal.append(x)
            elif x > pivot:
                greater.append(x)

        # Don't forget to return something!
        return sort(less) + equal + sort(greater)  # Just use the + operator to join lists

    # Note that you want equal ^^^^^ not pivot
    else:  # You need to handle the part at the end of the recursion - when you only
           # have one element in your array, just return the array.
        return array


print(sort())
