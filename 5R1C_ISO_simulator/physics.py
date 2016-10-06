"""
=========================================
Physics Required to calculate sensible space heating and space cooling loads
EN-13970
=========================================
"""

import numpy as np


__author__ = "Gabriel Happle"
__modified__ = "Prageeth Jayathissa"
__copyright__ = "Copyright 2016, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Gabriel Happle"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Prageeth Jayathissa"
__email__ = "jayathissa@arch.ethz.ch"
__status__ = "Production"



"""
The equations presented here is this code are derived from ISO 13790 Annex C 



VARIABLE DEFINITION

theta_m_t: Medium temperature of the enxt time step 
theta_m_prev: Medium temperature from the previous time step
c_m: Thermal Capacitance of the medium 
h_tr_3: combined heat conductance, see function for definition
h_tr_em: Heat conductance from the outside through opaque elements TODO: Check this
phi_m_tot: see formula for the calculation, eq C.5 in standard

phi_m: Combination of internal and solar gains directly to the medium 
theta_e: External air temperature
phi_st: combination of internal and solar gains directly to the internal surface
h_tr_w: Heat transfer from the outside through windows, doors
h_tr_1: combined heat conductance, see function for definition
phi_ia: combination of internal and solar gains to the air 
phi_hc_nd: Heating and Cooling of the supply air
h_ve_adj: Ventilation heat transmission coefficient 
h_tr_2: combined heat conductance, see function for definition 

h_tr_is: Some heat transfer coefficient between the air and the inside surface TODO: Check this

H_tr_ms: Heat transfer coefficient between the internal surface temperature and the medium

theta_m: Some wierd average between the previous and current timestep of the medium TODO: Check this

"""


def calc_theta_m_t(theta_m_prev, c_m, h_tr_3, h_tr_em, phi_m_tot):

    # (C.4) in [C.3 ISO 13790]

    theta_m_t = (theta_m_prev((c_m/3600)-0.5*(h_tr_3+h_tr_em))) + phi_m_tot / ((c_m/3600)+0.5*(h_tr_3+h_tr_em))

    return theta_m_t


def calc_phi_m_tot(phi_m, h_tr_em, theta_e, h_tr_3, phi_st, h_tr_w, h_tr_1, phi_ia, phi_hc_nd, h_ve_adj, h_tr_2 ):

    # (C.5) in [C.3 ISO 13790]
    # h_ve = h_ve_adj and theta_sup = theta_e [9.3.2 ISO 13790]

    phi_m_tot = phi_m + h_tr_em*theta_e + \
                h_tr_3*(phi_st + h_tr_w*theta_e+h_tr_1*(((phi_ia+phi_hc_nd)/h_ve_adj)+theta_e))/h_tr_2


    return phi_m_tot


def calc_h_tr_1(h_ve_adj, h_tr_is):

    # (C.6) in [C.3 ISO 13790]

    h_tr_1 = 1/(1/h_ve_adj + 1/h_tr_is)

    return h_tr_1


def calc_h_tr_2(h_tr_1, h_tr_w):

    # (C.7) in [C.3 ISO 13790]

    h_tr_2 = h_tr_1 + h_tr_w

    return h_tr_2


def calc_h_tr_3(h_tr_2, h_tr_ms):

    # (C.8) in [C.3 ISO 13790]

    h_tr_3 = 1/(1/h_tr_2 + 1/h_tr_ms)

    return h_tr_3


def calc_theta_m(theta_m_t, theta_m_prev):

    # (C.9) in [C.3 ISO 13790]
    theta_m = (theta_m_t+theta_m_prev)/2

    return theta_m


def calc_theta_s(h_tr_ms, theta_m, phi_st, h_tr_w, theta_e, h_tr_1, phi_ia, phi_hc_nd, h_ve_adj):

    # (C.10) in [C.3 ISO 13790]
    # h_ve = h_ve_adj and theta_sup = theta_e [9.3.2 ISO 13790]
    theta_s = (h_tr_ms*theta_m+phi_st+h_tr_w*theta_e+h_tr_1*(theta_e+(phi_ia+phi_hc_nd)/h_ve_adj)) / \
              (h_tr_ms+h_tr_w+h_tr_1)

    return theta_s


def calc_theta_air(h_tr_is, theta_s, h_ve_adj, theta_e, phi_ia, phi_hc_nd):
    # (C.11) in [C.3 ISO 13790]
    # h_ve = h_ve_adj and theta_sup = theta_e [9.3.2 ISO 13790]

    theta_air = (h_tr_is * theta_s + h_ve_adj * theta_e + phi_ia + phi_hc_nd) / (h_tr_is + h_ve_adj)

    return theta_air

def calc_theta_op(theta_air, theta_s):

    # (C.12) in [C.3 ISO 13790]
    theta_op = 0.3 * theta_air + 0.7 * theta_s

    return theta_op


def calc_temperatures_crank_nicholson( phi_hc_nd, building_thermal_prop ):

    # calculates air temperature and operative temperature for a given heating/cooling load
    # section C.3 in [C.3 ISO 13790]

    # TODO: get properties
    phi_m = building_thermal_prop.phi_m
    h_tr_em = building_thermal_prop.h_tr_em
    theta_e = building_thermal_prop.theta_e 
    h_tr_3 = building_thermal_prop.h_tr_3
    phi_st = building_thermal_prop.phi_st
    h_tr_w = building_thermal_prop.h_tr_w
    h_tr_1 = building_thermal_prop.h_tr_1
    phi_ia = building_thermal_prop.phi_ia
    h_ve_adj = building_thermal_prop.h_ve_adj
    h_tr_2 = building_thermal_prop.h_tr_2
    theta_m_prev = building_thermal_prop.theta_m_prev
    c_m = building_thermal_prop.c_m
    h_tr_ms = building_thermal_prop.h_tr_ms 
    h_tr_is = building_thermal_prop.h_tr_is 


    phi_m_tot = calc_phi_m_tot(phi_m, h_tr_em, theta_e, h_tr_3, phi_st, h_tr_w, h_tr_1, phi_ia, phi_hc_nd, h_ve_adj,
                               h_tr_2)

    theta_m_t = calc_theta_m_t(theta_m_prev, c_m, h_tr_3, h_tr_em, phi_m_tot)

    theta_m = calc_theta_m(theta_m_t, theta_m_prev)

    theta_s = calc_theta_s(h_tr_ms, theta_m, phi_st, h_tr_w, theta_e, h_tr_1, phi_ia, phi_hc_nd, h_ve_adj)

    theta_air = calc_theta_air(h_tr_is, theta_s, h_ve_adj, theta_e, phi_ia, phi_hc_nd)

    theta_op = calc_theta_op(theta_air, theta_s)

    return theta_m_t, theta_air, theta_op




def has_heating_demand(building_thermal_prop, setpoints):

    # TODO get setpoints
    theta_int_h_set = None

    # step 1 in section C.4.2 in [C.3 ISO 13790]

    # set heating cooling power to zero
    phi_hc_nd = 0

    # only air temperature is used for the check
    theta_air = calc_temperatures_crank_nicholson(phi_hc_nd, building_thermal_prop)[1]

    if theta_int_h_set <= theta_air:
        return False

    elif theta_air < theta_int_h_set:
        return True


def has_cooling_demand(building_thermal_prop, setpoints):

    # TODO get setpoints
    theta_int_c_set = None

    # step 1 in section C.4.2 in [C.3 ISO 13790]

    # set heating cooling power to zero
    phi_hc_nd = 0

    # only air temperature is used for the check
    theta_air = calc_temperatures_crank_nicholson(phi_hc_nd, building_thermal_prop)[1]

    if theta_int_c_set >= theta_air:
        return False

    elif theta_air > theta_int_c_set:
        return True


def calc_phi_hc_nd_un(phi_hc_nd_10, theta_air_set, theta_air_0, theta_air_10):

    # calculates unrestricted heating power
    # (C.13) in [C.3 ISO 13790]

    phi_hc_nd_un = phi_hc_nd_10*(theta_air_set - theta_air_0)/(theta_air_10 - theta_air_0)

    return phi_hc_nd_un


def calc_phi_hc_ac(building_thermal_prop):

    # Crank-Nicholson calculation procedure if heating/cooling system is active
    # Step 1 - Step 4 in Section C.4.2 in [C.3 ISO 13790]

    # Step 1:
    phi_hc_nd_0 = 0
    temp_rc_0 = calc_temperatures_crank_nicholson(phi_hc_nd_0, building_thermal_prop)
    theta_air_0 = temp_rc_0[1]

    # Step 2:
    theta_int_set = 20 # TODO: get setpoint
    af = 100 # TODO: get A_f

    theta_air_set = theta_int_set
    phi_hc_nd_10 = 10 * af

    temp_rc_10 = calc_temperatures_crank_nicholson(phi_hc_nd_10, building_thermal_prop)
    theta_air_10 = temp_rc_10[1]
    phi_hc_nd_un = calc_phi_hc_nd_un(phi_hc_nd_10,theta_air_set, theta_air_0, theta_air_10)

    # Step 3:
    phi_c_max = 100 # TODO: get max cooling power
    phi_h_max = 100 # TODO: get max heating power

    if phi_c_max <= phi_hc_nd_un <= phi_h_max:

        phi_hc_nd_ac = phi_hc_nd_un
        theta_air_ac = theta_air_set

    # Step 4:
    elif phi_hc_nd_un > phi_h_max: # necessary heating power exceeds maximum available power

        phi_hc_nd_ac = phi_h_max

    elif phi_hc_nd_un < phi_c_max: # necessary cooling power exceeds maximum available power

        phi_hc_nd_ac = phi_c_max

    else: # unknown situation

        phi_hc_nd_ac = 0
        print('ERROR: unknown radiative heating/cooling system status')


    # calculate system temperatures for Step 3/Step 4
    temp_ac = calc_temperatures_crank_nicholson(phi_hc_nd_ac, building_thermal_prop)

    theta_m_t_ac = temp_ac[0]
    theta_air_ac = temp_ac[1]  # should be the same as theta_air_set in the first case
    theta_op_ac = temp_ac[2]

    # exit calculation
    return theta_m_t_ac, theta_air_ac, theta_op_ac, phi_hc_nd_ac





def procedure_1(hoy, bpr, building_thermal_prop, setpoints):

    # building thermal properties at previous time step
    # +++++++++++++++++++++++++++++++++++++++++++++++++
    theta_m_prev = None

    # environmental properties
    # ++++++++++++++++++++++++
    theta_e = None

    # air flows
    # +++++++++
    m_ve_mech = None
    m_ve_window = None
    m_ve_leakage = None

    # air supply temperatures (HEX)
    # +++++++++++++++++++++++++++++
    temp_ve_mech = None

    # R-C-model properties
    # ++++++++++++++++++++
    phi_m = None
    phi_ia = None
    phi_st = None

    c_m = None

    h_tr_em = None
    h_tr_w = None
    h_ve_adj = None
    h_tr_ms = None
    h_tr_is = None

    h_tr_1 = calc_h_tr_1(h_ve_adj, h_tr_is)
    h_tr_2 = calc_h_tr_2(h_tr_1, h_tr_w)
    h_tr_3 = calc_h_tr_3(h_tr_2, h_tr_ms)

    # check demand
    # ++++++++++++
    if not has_heating_demand(building_thermal_prop, setpoints) and not has_cooling_demand(building_thermal_prop, setpoints):

        # no heating or cooling demand
        # calculate temperatures of building R-C-model and exit
        # --> rc_model_function_1(...)
        phi_hc_nd = 0
        temp_rc = calc_temperatures_crank_nicholson( phi_hc_nd, building_thermal_prop )

        theta_m_t = temp_rc[0]
        theta_air = temp_rc[1]
        theta_op = temp_rc[2]

        q_hs_sen_incl_em_loss = 0
        em_loss_hs = 0
        q_cs_sen_incl_em_loss = 0
        em_loss_cs = 0

        # return
        return

    elif has_heating_demand (building_thermal_prop, setpoints):

        # has heating demand
        # check if heating system is turned on

        if not control.is_heating_active(hoy, bpr):

            # no heating
            # calculate temperatures of building R-C-model and exit
            # --> rc_model_function_1(...)
            phi_hc_nd = 0
            temp_rc = calc_temperatures_crank_nicholson(phi_hc_nd, building_thermal_prop)

            theta_m_t = temp_rc[0]
            theta_air = temp_rc[1]
            theta_op = temp_rc[2]

            q_hs_sen_incl_em_loss = 0
            em_loss_hs = 0
            q_cs_sen_incl_em_loss = 0
            em_loss_cs = 0

            # return # TODO: check speed with and without return here
            # return

        elif control.is_heating_active(hoy, bpr) and control.heating_system_is_ac(bpr):

            # heating with AC
            # calculate loads and enter AC calculation
            # --> r_c_model_function_3(...)
            # --> kaempf_ac(...)
            # --> (iteration of air flows)
            # TODO: HVAC model

        elif control.is_heating_active(hoy, bpr) and control.heating_system_is_radiative(bpr):

            # heating with radiative system
            # calculate loads and emission losses
            # --> rc_model_function_2(...)
            theta_m_t_ac,\
            theta_air_ac,\
            theta_op_ac,\
            phi_hc_nd_ac = calc_phi_hc_ac(building_thermal_prop)

            # TODO: losses
            # TODO: how to calculate losses if phi_h_ac is phi_h_max ???

    elif has_cooling_demand(building_thermal_prop, setpoints):

        # has cooling demand
        # check if cooling system is turned on

        if not control.is_cooling_active(hoy, bpr):

            # no cooling
            # calculate temperatures of R-C-model and exit
            # --> rc_model_function_1(...)
            phi_hc_nd = 0
            temp_rc = calc_temperatures_crank_nicholson(phi_hc_nd, building_thermal_prop)

            theta_m_t = temp_rc[0]
            theta_air = temp_rc[1]
            theta_op = temp_rc[2]

            q_hs_sen_incl_em_loss = 0
            em_loss_hs = 0
            q_cs_sen_incl_em_loss = 0
            em_loss_cs = 0

            # return # TODO: check speed with and without return here
            # return

        elif control.is_cooling_active(hoy, bpr) and control.cooling_system_is_ac(bpr):

            # cooling with AC
            # calculate load and enter AC calculation
            # --> r_c_model_function_3(...)
            # --> kaempf_ac(...)
            # --> (iteration of air flows)
            # TODO: HVAC model

        elif control.is_cooling_active(hoy, bpr) and control.cooling_system_is_radiative(bpr):

            # cooling with radiative system
            # calculate loads and emission losses
            # --> rc_model_function_2(...)
            theta_m_t_ac, \
            theta_air_ac, \
            theta_op_ac, \
            phi_hc_nd_ac = calc_phi_hc_ac(building_thermal_prop)

            # TODO: losses

    else:
        print('Error: Unknown HVAC system status')
        return

    return












# TODO: night flushing: 9.3.3.10 in ISO 13790