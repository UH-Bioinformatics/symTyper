#!/usr/bin/python

from Bio import SearchIO
import os 
from Helpers import printVerbose

class CladeParser(object):
    def __init__(self, inFile, outputDirPath, minEval=1e-20, minFracLength = 0.87):
        self.inFile = inFile
        self.outputDirPath = outputDirPath
        self.minEval= minEval
        self.minFracLength = minFracLength

    def run(self):
        printVerbose("+++++"+self.outputDirPath+"++++++")
        lowFile  = open(os.path.join(self.outputDirPath, "LOW"), 'w')
        ambiguousFile = open(os.path.join(self.outputDirPath, "AMBIGUOUS"), 'w')
        hitsFile = open(os.path.join(self.outputDirPath, "HIT"), 'w')
        noHitsFile = open(os.path.join(self.outputDirPath, "NOHIT"), 'w')
        for seq in SearchIO.parse(self.inFile, 'hmmer3-text'):
            if len(seq.hits) >= 1:
                # DLS this check needs to be assured at least 1 hit exists!
                aliLen = sum([len(f) for f in seq.hits[0].fragments])           
                # if hits are short, log it and continue to the next seq.                                                                                                          
                if float(aliLen)/seq.seq_len < self.minFracLength:
                    noHitsFile.write("seqId:%s\n" % (seq.id) )
                    #continue
                elif seq.hits[0].evalue > self.minEval:
                    lowFile.write("LOW:%s\t%s\t%s\n" % (seq.id, seq.hits[0].id, seq.hits[0].evalue))
                    #continue
                else:
                    if len(seq.hits) > 1:
                        if (seq.hits[1].evalue / seq.hits[0].evalue) < 1e5:                
                            ambiguousFile.write("AMBIGUOUS:%s\t%s\t%s\t%s\t%s\n"
                                                % (seq.id, seq.hits[0].id, seq.hits[1].id, seq.hits[0].evalue, seq.hits[1].evalue))
                            #continue
                        else:
                            # DLS previously did not verify we had more than 1 hit, as a result we had index out of bound errors
                            # I corrected this by making an else case and adding annother else case if we only have 1 hit (make it a NOHIT)
                            #previous continue shortcircuits the following
                            hitsFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n"
                                           % (seq.id, seq.hits[0].hsps[0].query_start, seq.hits[0].hsps[0].query_end,  
                                              seq.hits[0].id, seq.hits[1].id, seq.hits[0].evalue, seq.hits[1].evalue))
                            #continue
                    else:
                        noHitsFile.write("seqId:%s\n" % (seq.id) )
            else:
                noHitsFile.write("seqId:%s\n" % (seq.id) )
                #continue
        lowFile.close(); ambiguousFile.close(); hitsFile.close(); noHitsFile.close()        
    
    def dryRun(self):
        return   "parsing hmmer out  for file %s and putting results in %s" % (self.inFile, self.outputDirPath)
    
