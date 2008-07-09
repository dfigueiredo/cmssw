#include <functional>
#include <algorithm>
#include <string>
#include <vector>

#include <TString.h>
#include <TTree.h>

#include "FWCore/Utilities/interface/Exception.h"

#include "PhysicsTools/MVAComputer/interface/MVAComputer.h"
#include "PhysicsTools/MVAComputer/interface/TreeReader.h"

#include "PhysicsTools/MVATrainer/interface/MVATrainer.h"
#include "PhysicsTools/MVATrainer/interface/TreeTrainer.h"

namespace PhysicsTools {

TreeTrainer::TreeTrainer()
{
}

TreeTrainer::TreeTrainer(TTree *tree)
{
	addTree(tree);
}

TreeTrainer::TreeTrainer(TTree *signal, TTree *background)
{
	addTree(signal, true);
	addTree(background, false);
}

TreeTrainer::~TreeTrainer()
{
	reset();
}

Calibration::MVAComputer *TreeTrainer::train(const std::string &trainFile)
{
	MVATrainer trainer(trainFile);
	train(&trainer);
	return trainer.getCalibration();
}

void TreeTrainer::reset()
{
	readers.clear();
	std::for_each(weights.begin(), weights.end(),
	              std::ptr_fun(&::operator delete));
	weights.clear();
}

void TreeTrainer::addTree(TTree *tree, int target, double weight)
{
	static const bool targets[2] = { true, false };

	TreeReader reader(tree);

	if (target >= 0)
		reader.addSingle(MVATrainer::kTargetId, &targets[!target]);

	if (weight > 0.0) {
		double *ptr = new double(weight);
		weights.push_back(ptr);
		reader.addSingle(MVATrainer::kWeightId, ptr);
	}

	addReader(reader);
}

void TreeTrainer::addReader(const TreeReader &reader)
{
	readers.push_back(reader);
}

bool TreeTrainer::iteration(MVATrainer *trainer)
{
	Calibration::MVAComputer *calib = trainer->getTrainCalibration();   
	if (!calib)
		return true;

	MVAComputer computer(calib, true);

	std::for_each(readers.begin(), readers.end(),
	              std::bind2nd(std::mem_fun_ref(&TreeReader::loop),
	                           &computer));

	return false;
}

void TreeTrainer::train(MVATrainer *trainer)
{
	while(!iteration(trainer));
}

} // namespace PhysicsTools
