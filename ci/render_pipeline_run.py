#!/usr/bin/env python3

import argparse
import dataclasses
import yaml

import glci.model
import tkn.model

GardenlinuxFlavour = glci.model.GardenlinuxFlavour

PipelineRef = tkn.model.PipelineRef
PipelineRun = tkn.model.PipelineRun
PipelineRunSpec = tkn.model.PipelineRunSpec
PipelineRunMetadata = tkn.model.PipelineRunMetadata
PipelineMetadata = tkn.model.PipelineMetadata
PodTemplate = tkn.model.PodTemplate
TaskRef = tkn.model.TaskRef
PipelineTask = tkn.model.PipelineTask
NamedParam = tkn.model.NamedParam


def mk_pipeline_run(
    pipeline_name: str,
    namespace: str,
    committish: str,
    cicd_cfg: str,
):
    run_name = f'{pipeline_name}-{committish}'[:60] # k8s length restriction

    plrun = PipelineRun(
        metadata=PipelineRunMetadata(
            name=run_name,
            namespace=namespace,
        ),
        spec=PipelineRunSpec(
            params=[
                NamedParam(
                    name='committish',
                    value=committish,
                ),
                NamedParam(
                    name='cicd_cfg_name',
                    value=cicd_cfg,
                ),
            ],
            pipelineRef=PipelineRef(
                name=pipeline_name,
            ),
            podTemplate=PodTemplate(
                nodeSelector={
                    "worker.garden.sapcloud.io/group": "gl-build"
                }
            )
        ),
    )
    return plrun


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--committish', default='master')
    parser.add_argument('--cicd-cfg', default='default')
    parser.add_argument('--outfile', default='pipeline_run.yaml')

    parsed = parser.parse_args()

    # XXX hardcode pipeline names and flavour for now
    pipeline_run = mk_pipeline_run(
        pipeline_name='build-gardenlinux-snapshot-pipeline',
        namespace='gardenlinux-tkn',
        committish=parsed.committish,
        cicd_cfg=parsed.cicd_cfg,
    )

    pipeline_run_dict = dataclasses.asdict(pipeline_run)

    with open(parsed.outfile, 'w') as f:
        yaml.safe_dump(pipeline_run_dict, f)

    print(f'pipeline-run written to {parsed.outfile}')


if __name__ == '__main__':
    main()