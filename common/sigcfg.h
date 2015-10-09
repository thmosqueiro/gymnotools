#ifndef SIGCFG_H
#define SIGCFG_H

/*
 * Base settings
 */

static const int NumChannels = 11;
static const double SamplingRate = 50000.0;
static const int EODSamples = 128;

/*
 * Derived settings
 */

static const int BytesPerSample = NumChannels * sizeof(float);


#endif // SIGCFG_H
