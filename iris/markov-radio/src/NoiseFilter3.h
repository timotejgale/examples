/* 
 * File:   NoiseFilter2.h
 * Author: ctvr
 *
 * Created on August 31, 2015, 5:05 PM
 */

#ifndef NOISEFILTER3_H
#define	NOISEFILTER3_H

#include "KHMO2.h"
#include "stats.h"
#include <boost/format.hpp>
#include <sstream>

class NoiseFilter3 
{
public:
    NoiseFilter3(uint16_t _Nch, float _alpha = 0.001, float _thres = 7) : Nch(_Nch), min_limit(1e-9) // thres is in dB!
    {
        clusterizers.assign(Nch, KHMO2(2, 2, _alpha, _thres));
        noise_hits_stats.resize(Nch,rate_stats());
    }
    void filter(std::vector<float> &ch_pwr)
    { // Warning: may change ch_pwr
        
        size_t clus_idx, noise_idx;
        for (register uint16_t i = 0; i < Nch; i++)
        {
            double dB_val = 10*log10(ch_pwr[i]);
            if(ch_pwr[i] > min_limit)               // cut off the NaN crap to not skew average
            {
                clus_idx = clusterizers[i].push(dB_val);
            }
            else
            {
                ch_pwr[i] = 0;
                continue;
            }
            
            noise_idx = ch_noise_floor_idx(i);
            //if(clus_idx == noise_idx && 7 < (dB_val - ch_noise_floor(i)))
            //    clus_idx = (clus_idx + 1) % 2;
            
            if(clus_idx == noise_idx)    // if the new sample is just noise
            //if(ch_pwr[i] < 3 + ch_noise_floor(i))
            {
                ch_pwr[i] = 0;
                noise_hits_stats[i].miss();
            }
            else
            {
                noise_hits_stats[i].hit();
            }
        }
    }
    
    void reset() 
    {
        for (uint16_t i = 0; i < Nch; i++) 
        {
            clusterizers[i].clusters.clear();
            noise_hits_stats[i].reset();
        }
    }
    void set_thres(float _thres) 
    {
        thres = _thres;
        reset();
    }
    double estimated_noise_floor()
    {
        double sum = 0;
        for(int i = 0; i < clusterizers.size(); ++i)
        {
            sum += ch_noise_floor(i);
        }
        return sum / Nch;
    }
    inline float ch_noise_floor(uint16_t idx) 
    {
        return (clusterizers[idx].clusters.size() > 0) ? std::min_element(clusterizers[idx].clusters.begin(), clusterizers[idx].clusters.end(), 
        [](const KHMO2::KHMOCluster &a, const KHMO2::KHMOCluster &b){
            return a.mk < b.mk;
        })->mk : -90;
    }
    inline float ch_sig_power(uint16_t idx) 
    {
        return (clusterizers[idx].clusters.size() > 1) ? std::max_element(clusterizers[idx].clusters.begin(), clusterizers[idx].clusters.end(), 
        [](const KHMO2::KHMOCluster &a, const KHMO2::KHMOCluster &b){
            return a.mk < b.mk;
        })->mk : -90;
    }
    inline int ch_noise_floor_idx(uint16_t idx)
    {
        return (clusterizers[idx].clusters.size() > 0) ? std::distance(clusterizers[idx].clusters.begin(), std::min_element(clusterizers[idx].clusters.begin(), clusterizers[idx].clusters.end(), 
        [](const KHMO2::KHMOCluster &a, const KHMO2::KHMOCluster &b){
            return a.mk < b.mk;
        })) : -1;
    }
    inline float ch_detec_rate(uint16_t idx) 
    {
        return (noise_hits_stats[idx].val_count > 0) ? noise_hits_stats[idx].get_rate() : 0;
    }
    std::string print_ch_sig_power() 
    {
        std::stringstream ss;
        for (int i = 0; i < Nch; i++) {
            float pwr = ch_sig_power(i);
            if(pwr > -90)
                ss << boost::format("%d: %.4f") % i % (ch_sig_power(i)) << " dB\t";
            else
                ss << boost::format("%d: No Signal") % i << " dB\t";
        }
        ss << "\n";
        return ss.str();
    }
    std::string print_ch_noise_floor() 
    {
        std::stringstream ss;
        for (int i = 0; i < Nch; i++) {
            ss << boost::format("%d: %.4f") % i % (ch_noise_floor(i)) << " dB\t";
        }
        ss << "\n";
        return ss.str();
    }
    std::string print_ch_pdetec() 
    {
        std::stringstream ss;
        for (int i = 0; i < Nch; i++) {
            ss << boost::format("%d: %.4f") % i % (ch_detec_rate(i) * 100) << "%\t";
        }
        ss << "\n";
        return ss.str();
    }
    std::vector<KHMO2> clusterizers;
    double min_limit;
private:
    uint16_t Nch;
    float thres;
    std::vector<rate_stats> noise_hits_stats;
};

// This class is used to make SU jump to previous PU channel
class PURegister
{
    int last_channel;
public:
    
    PURegister() : last_channel(0)
    {
    }
    
    /**
     * If all ch_pwr==0, return "last_channel"
     * Otherwise, change last channel to the one with highest power and return -1
     */
    int hopping_required(const std::vector<float> &ch_pwr)
    {
        int numfree = 0;
        float max_val_idx = 0;
        for (int i = 0; i < ch_pwr.size(); i++)
        {
            if (ch_pwr[i] == 0)
            {
                numfree++;
                continue;
            }
            if(ch_pwr[max_val_idx] < ch_pwr[i])
                max_val_idx = i;
        }
        
        if(numfree == ch_pwr.size())
        {
            return last_channel;
        }
        else
        {
            last_channel = max_val_idx;
            return -1;
        }
    }
};

#endif	/* NOISEFILTER3_H */
