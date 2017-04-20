testCases=`ls case*`
echo $testCases
for file in $testCases
do
	outputName="output_"${file}
	echo "Running file : ${file}"
	cp $file input.txt
	#cat input.txt
	startTime=`date +"%M%S.%3N"`
	python homework.py > /dev/null
	endTime=`date +"%M%S.%3N"`
	diff=`comm -3 output.txt ${outputName}`
	if [ ! -z "$diff" ]; then
		echo $diff
		echo "output :"
		cat output.txt
		echo "Expected output:"
		cat $outputName
	else
		echo "Case PASSED"
		timeTaken=`echo "$endTime-$startTime" | bc`
		echo "Time taken in seconds : $timeTaken"
	fi
done
exit
