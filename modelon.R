modelon<-function(p_id){
  loandata<-read.csv(paste0("data/Rin/",p_id,".csv"),header=FALSE)
  print(loandata)

  write(1.00,file=paste0("data/Rout/",p_id))
}
