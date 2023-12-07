def calculate_checksum(signal_value):

    # Initial conditions
    initial_signal = 7828
    initial_checksum = 28
    modulo_value = 63
    increments = [3, 2, 3, 3, 2, 3, 3, 2, 3, 3, 2, 3, 3, 1, 2, 2, 3, 3, 2, 3, 3, 2, 3, 3, 2]
    # Calculate the number of steps from the initial signal
    steps = (signal_value) - initial_signal

    # Initialize the checksum
    checksum = initial_checksum

    # Apply the increments or decrements in a cycle
    for i in range(abs(steps)):
        increment = increments[i % len(increments)]
        if i == abs(steps)-1:
            #print(i % len(increments))
            pass
        if steps >= 0:
            # Incrementing for higher signal values
            if checksum == modulo_value: # special case when the checksum rolls over the pattern changes
                checksum = 0
            else:
                checksum += increment
                if checksum > modulo_value:
                    checksum = modulo_value
        else:
            # Decrementing for lower signal values
            checksum -= increment
            if checksum < 0:
                checksum = modulo_value
    
    return checksum


# Test the function for a range of values
for signal in range(7828, 8658):
    print(f"Signal: {signal}, Checksum: {calculate_checksum(signal)}")


# This is the output from this script in its current state:
# Signal: 7828, Checksum: 28
# Signal: 7829, Checksum: 31
# Signal: 7830, Checksum: 34
# Signal: 7831, Checksum: 36
# Signal: 7832, Checksum: 39
# Signal: 7833, Checksum: 42
# Signal: 7834, Checksum: 44
# Signal: 7835, Checksum: 47
# Signal: 7836, Checksum: 50
# Signal: 7837, Checksum: 52
# Signal: 7838, Checksum: 55
# Signal: 7839, Checksum: 58
# Signal: 7840, Checksum: 60
# Signal: 7841, Checksum: 63
# Signal: 7842, Checksum: 2
# Signal: 7843, Checksum: 4
# Signal: 7844, Checksum: 7
# more values ...

# you can see when Signal = 7844 the 'checksum' is 7 but it should be 4 (see the data[] list below). When 'signal' is 7843 the 'checksum' 
# is 4 so we can try to subtract 1 from the provided 'signal' before we do the calculation to offset it. 
# Doing this would cause all the previous values to be off by 1 'increment'. So one idea is to increase the offset as 'signal' increases. 
'''
offset = signal_value//23
signal_value -= offset
'''
# But if you try that you get the same checksum value twice in a row for example:
'''
Signal: 7836, Checksum: 50
Signal: 7837, Checksum: 52
Signal: 7838, Checksum: 55
Signal: 7839, Checksum: 58
Signal: 7840, Checksum: 60 
Signal: 7841, Checksum: 60 <--
...
Signal: 8102, Checksum: 31
Signal: 8103, Checksum: 34
Signal: 8104, Checksum: 36
Signal: 8105, Checksum: 36 <--
'''

# Here is a snippet of real data collected from the vehicles canbus with the format [14 bit signal, 7 bit checksum with pattern].
# There are gaps in the value of the 14 bit signal value (7833, 7834, 7837, 7838, 7844). 
# I have sorted them from least to greatest and removed duplicates using the script below (not important but just FYI):
'''
unique_list = [list(x) for x in set(tuple(x) for x in data)]
sorted_list = sorted(unique_list, key=lambda x: x[0])

for itm in sorted_list:
    print(i)
''' 
# This is the real data:
# data = [[7828, 28]
# [7829, 31]
# [7830, 34]
# [7831, 36]
# [7833, 42]
# [7834, 44]
# [7837, 52]
# [7838, 55]
# [7844, 4]
# [7846, 10]
# [7854, 31]
# [7855, 34]
# [7859, 44]
# [7870, 7]
# [7871, 10]
# [7883, 42]
# [7889, 58]
# [7895, 7]
# [7902, 26]
# [7916, 63]
# [7924, 18]
# [7926, 23]
# [7940, 60]
# [7952, 26]
# [7955, 34]
# [7961, 50]
# [7965, 60]
# [7976, 23]
# [7988, 55]
# [7991, 63]
# [7995, 7]
# [8007, 39]
# [8015, 60]
# [8021, 10]
# [8027, 26]
# [8030, 34]
# [8040, 60]
# [8048, 15]
# [8051, 23]
# [8057, 39]
# [8068, 2]
# [8072, 12]
# [8078, 28]
# [8079, 31]
# [8097, 12]
# [8098, 15]
# [8103, 28]
# [8105, 34]
# [8106, 36]
# [8108, 42]
# [8110, 47]
# [8112, 52]
# [8116, 63]
# [8119, 4]
# [8120, 7]
# [8121, 10]
# [8122, 12]
# [8123, 15]
# [8126, 23]
# [8127, 26]
# [8128, 28]
# [8130, 34]
# [8131, 36]
# [8132, 39]
# [8134, 44]
# [8135, 47]
# [8136, 50]
# [8137, 52]
# [8139, 58]
# [8140, 60]
# [8141, 63]
# [8143, 2]
# [8144, 4]
# [8145, 7]
# [8146, 10]
# [8147, 12]
# [8148, 15]
# [8149, 18]
# [8150, 20]
# [8151, 23]
# [8152, 26]
# [8153, 28]
# [8154, 31]
# [8155, 34]
# [8156, 36]
# [8157, 39]
# [8168, 2]
# [8172, 12]
# [8174, 18]
# [8182, 39]
# [8184, 44]
# [8186, 50]
# [8195, 7]
# [8196, 10]
# [8202, 26]
# [8211, 50]
# [8219, 4]
# [8223, 15]
# [8232, 39]
# [8233, 42]
# [8235, 47]
# [8245, 7]
# [8251, 23]
# [8255, 34]
# [8268, 2]
# [8271, 10]
# [8276, 23]
# [8277, 26]
# [8287, 52]
# [8295, 7]
# [8298, 15]
# [8300, 63]
# [8309, 44]
# [8312, 52]
# [8315, 60]
# [8319, 4]
# [8325, 20]
# [8330, 34]
# [8334, 44]
# [8340, 60]
# [8343, 2]
# [8344, 4]
# [8352, 26]
# [8359, 44]
# [8361, 50]
# [8364, 58]
# [8365, 60]
# [8366, 63]
# [8368, 2]
# [8369, 4]
# [8371, 10]
# [8374, 18]
# [8380, 34]
# [8382, 39]
# [8384, 44]
# [8385, 47]
# [8386, 50]
# [8395, 7]
# [8398, 15]
# [8399, 18]
# [8404, 31]
# [8407, 39]
# [8411, 50]
# [8415, 60]
# [8416, 63]
# [8421, 10]
# [8422, 12]
# [8424, 18]
# [8425, 20]
# [8427, 26]
# [8429, 31]
# [8430, 34]
# [8441, 63]
# [8448, 15]
# [8463, 55]
# [8465, 60]
# [8477, 26]
# [8495, 7]
# [8500, 20]
# [8511, 50]
# [8526, 23]
# [8536, 50]
# [8541, 63]
# [8560, 47]
# [8571, 10]
# [8572, 12]
# [8593, 2]
# [8599, 18]
# [8611, 50]
# [8620, 7]
# [8633, 42]
# [8636, 50]
# [8644, 4]
# [8647, 12]
# [8648, 15]
# [8653, 28]
# [8654, 31]
# [8656, 36]
# [8657, 39]
# [8658, 42]]

