#include "compilerspecific.h"
#include "wfilts.h"

static float daub7_h[] ALIGN(16) = {
     0.077852054085062,  0.396539319482306,  0.729132090846555,  0.469782287405359, -0.143906003929106,
    -0.224036184994166,  0.071309219267050,  0.080612609151066, -0.038029936935035, -0.016574541631016,
     0.012550998556014,  0.000429577973005, -0.001801640704000,  0.000353713800001,
};
static float daub7_g[] ALIGN(16) = {
     0.000353713800001,  0.001801640704000,  0.000429577973005, -0.012550998556014, -0.016574541631016,
     0.038029936935035,  0.080612609151066, -0.071309219267050, -0.224036184994166,  0.143906003929106,
     0.469782287405359, -0.729132090846555,  0.396539319482306, -0.077852054085062,
};
static float qshf1_h[] ALIGN(16) = {
     0.002609700261841,  0.000162258390311,  0.001119301593802, -0.009664912468810,  0.005899523559559,
     0.045354650419414, -0.054114477755699, -0.112198503754835,  0.280910663006716,  0.753010936948491,
     0.565293214806365,  0.025430612869708, -0.121306068933115,  0.016053537034447,  0.032097264389903,
    -0.010668398638807, -0.005492754446412,  0.001081141079834,  0.000090433585293, -0.001454525937692,
};
static float qshf1_g[] ALIGN(16) = {
    -0.001454525937692, -0.000090433585293,  0.001081141079834,  0.005492754446412, -0.010668398638807,
    -0.032097264389903,  0.016053537034447,  0.121306068933115,  0.025430612869708, -0.565293214806365,
     0.753010936948491, -0.280910663006716, -0.112198503754835,  0.054114477755699,  0.045354650419414,
    -0.005899523559559, -0.009664912468810, -0.001119301593802,  0.000162258390311, -0.002609700261841,
};
static float qshf2_h[] ALIGN(16) = {
    -0.001454525937692,  0.000090433585293,  0.001081141079834, -0.005492754446412, -0.010668398638807,
     0.032097264389903,  0.016053537034447, -0.121306068933115,  0.025430612869708,  0.565293214806365,
     0.753010936948491,  0.280910663006716, -0.112198503754835, -0.054114477755699,  0.045354650419414,
     0.005899523559559, -0.009664912468810,  0.001119301593802,  0.000162258390311,  0.002609700261841,
};
static float qshf2_g[] ALIGN(16) = {
    -0.002609700261841,  0.000162258390311, -0.001119301593802, -0.009664912468810, -0.005899523559559,
     0.045354650419414,  0.054114477755699, -0.112198503754835, -0.280910663006716,  0.753010936948491,
    -0.565293214806365,  0.025430612869708,  0.121306068933115,  0.016053537034447, -0.032097264389903,
    -0.010668398638807,  0.005492754446412,  0.001081141079834, -0.000090433585293, -0.001454525937692,
};
static wavelet_filt daub7  = { 14,  -7, daub7_h, daub7_g };
static wavelet_filt daub7s = { 14,  -8, daub7_h, daub7_g };
static wavelet_filt qshf1  = { 20, -10, qshf1_h, qshf1_g };
static wavelet_filt qshf2  = { 20, -10, qshf2_h, qshf2_g };
cwpt_filt tree1_filt = { &daub7,  &qshf1, &daub7 };
cwpt_filt tree2_filt = { &daub7s, &qshf2, &daub7 };

