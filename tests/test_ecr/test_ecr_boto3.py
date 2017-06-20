from __future__ import unicode_literals

import hashlib
import json
from random import random

import sure  # noqa

import boto3

from moto import mock_ecr


def _create_image_digest(contents=None):
    if not contents:
        contents = 'docker_image{0}'.format(int(random() * 10 ** 6))
    return "sha256:%s" % hashlib.sha256(contents.encode('utf-8')).hexdigest()


def _create_image_manifest():
    return {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "config":
            {
                "mediaType": "application/vnd.docker.container.image.v1+json",
                "size": 7023,
                "digest": _create_image_digest("config")
            },
        "layers": [
            {
                "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                "size": 32654,
                "digest": _create_image_digest("layer1")
            },
            {
                "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                "size": 16724,
                "digest": _create_image_digest("layer2")
            },
            {
                "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                "size": 73109,
                "digest": _create_image_digest("layer3")
            }
        ]
    }


@mock_ecr
def test_create_repository():
    client = boto3.client('ecr', region_name='us-east-1')
    response = client.create_repository(
        repositoryName='test_ecr_repository'
    )
    response['repository']['repositoryName'].should.equal('test_ecr_repository')
    response['repository']['repositoryArn'].should.equal(
        'arn:aws:ecr:us-east-1:012345678910:repository/test_ecr_repository')
    response['repository']['registryId'].should.equal('012345678910')
    response['repository']['repositoryUri'].should.equal(
        '012345678910.dkr.ecr.us-east-1.amazonaws.com/test_ecr_repository')
    # response['repository']['createdAt'].should.equal(0)


@mock_ecr
def test_describe_repositories():
    client = boto3.client('ecr', region_name='us-east-1')
    _ = client.create_repository(
        repositoryName='test_repository1'
    )
    _ = client.create_repository(
        repositoryName='test_repository0'
    )
    response = client.describe_repositories()
    len(response['repositories']).should.equal(2)

    respository_arns = ['arn:aws:ecr:us-east-1:012345678910:repository/test_repository1',
                        'arn:aws:ecr:us-east-1:012345678910:repository/test_repository0']
    set([response['repositories'][0]['repositoryArn'],
         response['repositories'][1]['repositoryArn']]).should.equal(set(respository_arns))

    respository_uris = ['012345678910.dkr.ecr.us-east-1.amazonaws.com/test_repository1',
                        '012345678910.dkr.ecr.us-east-1.amazonaws.com/test_repository0']
    set([response['repositories'][0]['repositoryUri'],
         response['repositories'][1]['repositoryUri']]).should.equal(set(respository_uris))


@mock_ecr
def test_describe_repositories_1():
    client = boto3.client('ecr', region_name='us-east-1')
    _ = client.create_repository(
        repositoryName='test_repository1'
    )
    _ = client.create_repository(
        repositoryName='test_repository0'
    )
    response = client.describe_repositories(registryId='012345678910')
    len(response['repositories']).should.equal(2)

    respository_arns = ['arn:aws:ecr:us-east-1:012345678910:repository/test_repository1',
                        'arn:aws:ecr:us-east-1:012345678910:repository/test_repository0']
    set([response['repositories'][0]['repositoryArn'],
         response['repositories'][1]['repositoryArn']]).should.equal(set(respository_arns))

    respository_uris = ['012345678910.dkr.ecr.us-east-1.amazonaws.com/test_repository1',
                        '012345678910.dkr.ecr.us-east-1.amazonaws.com/test_repository0']
    set([response['repositories'][0]['repositoryUri'],
         response['repositories'][1]['repositoryUri']]).should.equal(set(respository_uris))


@mock_ecr
def test_describe_repositories_2():
    client = boto3.client('ecr', region_name='us-east-1')
    _ = client.create_repository(
        repositoryName='test_repository1'
    )
    _ = client.create_repository(
        repositoryName='test_repository0'
    )
    response = client.describe_repositories(registryId='109876543210')
    len(response['repositories']).should.equal(0)


@mock_ecr
def test_describe_repositories_3():
    client = boto3.client('ecr', region_name='us-east-1')
    _ = client.create_repository(
        repositoryName='test_repository1'
    )
    _ = client.create_repository(
        repositoryName='test_repository0'
    )
    response = client.describe_repositories(repositoryNames=['test_repository1'])
    len(response['repositories']).should.equal(1)
    respository_arn = 'arn:aws:ecr:us-east-1:012345678910:repository/test_repository1'
    response['repositories'][0]['repositoryArn'].should.equal(respository_arn)

    respository_uri = '012345678910.dkr.ecr.us-east-1.amazonaws.com/test_repository1'
    response['repositories'][0]['repositoryUri'].should.equal(respository_uri)


@mock_ecr
def test_describe_repositories_4():
    client = boto3.client('ecr', region_name='us-east-1')
    _ = client.create_repository(
        repositoryName='test_repository1'
    )
    _ = client.create_repository(
        repositoryName='test_repository0'
    )
    response = client.describe_repositories(repositoryNames=['not_a_valid_name'])
    len(response['repositories']).should.equal(0)


@mock_ecr
def test_describe_repositories_with_image():
    client = boto3.client('ecr', region_name='us-east-1')
    _ = client.create_repository(
        repositoryName='test_repository'
    )

    _ = client.put_image(
        repositoryName='test_repository',
        imageManifest=json.dumps(_create_image_manifest()),
        imageTag='latest'
    )

    response = client.describe_repositories(repositoryNames=['test_repository'])
    len(response['repositories']).should.equal(1)


@mock_ecr
def test_delete_repository():
    client = boto3.client('ecr', region_name='us-east-1')
    _ = client.create_repository(
        repositoryName='test_repository'
    )
    response = client.delete_repository(repositoryName='test_repository')
    response['repository']['repositoryName'].should.equal('test_repository')
    response['repository']['repositoryArn'].should.equal(
        'arn:aws:ecr:us-east-1:012345678910:repository/test_repository')
    response['repository']['registryId'].should.equal('012345678910')
    response['repository']['repositoryUri'].should.equal(
        '012345678910.dkr.ecr.us-east-1.amazonaws.com/test_repository')
    # response['repository']['createdAt'].should.equal(0)

    response = client.describe_repositories()
    len(response['repositories']).should.equal(0)


@mock_ecr
def test_put_image():
    client = boto3.client('ecr', region_name='us-east-1')
    _ = client.create_repository(
        repositoryName='test_repository'
    )

    response = client.put_image(
        repositoryName='test_repository',
        imageManifest=json.dumps(_create_image_manifest()),
        imageTag='latest'
    )

    response['image']['imageId']['imageTag'].should.equal('latest')
    response['image']['imageId']['imageDigest'].should.contain("sha")
    response['image']['repositoryName'].should.equal('test_repository')
    response['image']['registryId'].should.equal('012345678910')


@mock_ecr
def test_list_images():
    client = boto3.client('ecr', region_name='us-east-1')
    _ = client.create_repository(
        repositoryName='test_repository_1'
    )

    _ = client.create_repository(
        repositoryName='test_repository_2'
    )

    _ = client.put_image(
        repositoryName='test_repository_1',
        imageManifest=json.dumps(_create_image_manifest()),
        imageTag='latest'
    )

    _ = client.put_image(
        repositoryName='test_repository_1',
        imageManifest=json.dumps(_create_image_manifest()),
        imageTag='v1'
    )

    _ = client.put_image(
        repositoryName='test_repository_1',
        imageManifest=json.dumps(_create_image_manifest()),
        imageTag='v2'
    )

    _ = client.put_image(
        repositoryName='test_repository_2',
        imageManifest=json.dumps(_create_image_manifest()),
        imageTag='oldest'
    )

    response = client.list_images(repositoryName='test_repository_1')
    type(response['imageIds']).should.be(list)
    len(response['imageIds']).should.be(3)

    image_tags = ['latest', 'v1', 'v2']
    set([response['imageIds'][0]['imageTag'],
         response['imageIds'][1]['imageTag'],
         response['imageIds'][2]['imageTag']]).should.equal(set(image_tags))

    response = client.list_images(repositoryName='test_repository_2')
    type(response['imageIds']).should.be(list)
    len(response['imageIds']).should.be(1)
    response['imageIds'][0]['imageTag'].should.equal('oldest')

    response = client.list_images(repositoryName='test_repository_2', registryId='109876543210')
    type(response['imageIds']).should.be(list)
    len(response['imageIds']).should.be(0)


@mock_ecr
def test_describe_images():
    client = boto3.client('ecr', region_name='us-east-1')
    _ = client.create_repository(
        repositoryName='test_repository'
    )

    _ = client.put_image(
        repositoryName='test_repository',
        imageManifest=json.dumps(_create_image_manifest()),
        imageTag='latest'
    )

    _ = client.put_image(
        repositoryName='test_repository',
        imageManifest=json.dumps(_create_image_manifest()),
        imageTag='v1'
    )

    _ = client.put_image(
        repositoryName='test_repository',
        imageManifest=json.dumps(_create_image_manifest()),
        imageTag='v2'
    )

    response = client.describe_images(repositoryName='test_repository')
    type(response['imageDetails']).should.be(list)
    len(response['imageDetails']).should.be(3)

    response['imageDetails'][0]['imageDigest'].should.contain("sha")
    response['imageDetails'][1]['imageDigest'].should.contain("sha")
    response['imageDetails'][2]['imageDigest'].should.contain("sha")

    response['imageDetails'][0]['registryId'].should.equal("012345678910")
    response['imageDetails'][1]['registryId'].should.equal("012345678910")
    response['imageDetails'][2]['registryId'].should.equal("012345678910")

    response['imageDetails'][0]['repositoryName'].should.equal("test_repository")
    response['imageDetails'][1]['repositoryName'].should.equal("test_repository")
    response['imageDetails'][2]['repositoryName'].should.equal("test_repository")

    len(response['imageDetails'][0]['imageTags']).should.be(1)
    len(response['imageDetails'][1]['imageTags']).should.be(1)
    len(response['imageDetails'][2]['imageTags']).should.be(1)

    image_tags = ['latest', 'v1', 'v2']
    set([response['imageDetails'][0]['imageTags'][0],
         response['imageDetails'][1]['imageTags'][0],
         response['imageDetails'][2]['imageTags'][0]]).should.equal(set(image_tags))

    response['imageDetails'][0]['imageSizeInBytes'].should.equal(52428800)
    response['imageDetails'][1]['imageSizeInBytes'].should.equal(52428800)
    response['imageDetails'][2]['imageSizeInBytes'].should.equal(52428800)
