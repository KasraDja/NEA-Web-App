def MergeSort(list):
    length = len(list)
    if length>1:
        righthalf = (length)//2
        lefthalf = righthalf
        righthalf = MergeSort(list[righthalf:])
        lefthalf = MergeSort(list[:lefthalf])
        sorted = []
        while len(righthalf) != 0 or len(lefthalf) != 0:
            if len(righthalf) == 0:
                sorted.extend(lefthalf)
                return sorted
            elif len(lefthalf) == 0:
                sorted.extend(righthalf)
                return sorted
            elif righthalf[0][2]>lefthalf[0][2]:
                sorted.append(lefthalf[0])
                del lefthalf[0]
            else:
                sorted.append(righthalf[0])
                del righthalf[0]
        return sorted
    else: return list