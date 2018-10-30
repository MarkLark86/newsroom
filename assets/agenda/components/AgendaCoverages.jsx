import React from 'react';
import PropTypes from 'prop-types';
import { isEmpty } from 'lodash';
import { gettext, formatCoverageDate } from 'utils';
import CoverageItemStatus from './CoverageItemStatus';
import {getCoverageDisplayName, getCoverageIcon, WORKFLOW_COLORS} from '../utils';


export default function AgendaCoverages({coverages}) {
    if (isEmpty(coverages)) {
        return null;
    }

    return coverages.map((coverage) => (
        <div className='coverage-item' key={coverage.coverage_id}>
            <div className='coverage-item__row'>
                <span className='d-flex coverage-item--element-grow text-overflow-ellipsis'>
                    <i className={`icon-small--coverage-${getCoverageIcon(coverage.coverage_type)} ${WORKFLOW_COLORS[coverage.workflow_status]} mr-2`}></i>
                    <span className='text-overflow-ellipsis'>{getCoverageDisplayName(coverage.coverage_type)}</span>
                </span>
                <span className='d-flex'>
                    <i className='icon-small--clock icon--gray mr-1'></i>
                    <span className='coverage-item__text-label mr-1'>{gettext('due by')}:</span>
                    <span>{formatCoverageDate(coverage.scheduled)}</span>
                </span>
            </div>

            <div className='coverage-item__row'>
                {coverage.coverage_provider && <span className='coverage-item__text-label mr-1'>{gettext('Source')}:</span>}
                {coverage.coverage_provider && <span className='mr-2'>{coverage.coverage_provider}</span>}
                <CoverageItemStatus coverage={coverage} />
            </div>
        </div>
    ));
}

AgendaCoverages.propTypes = {
    coverages: PropTypes.array,
};