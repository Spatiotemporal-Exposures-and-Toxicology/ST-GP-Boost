using NCDatasets, DataFrames, Missings, Plots, JLD2;
using Statistics, StatsBase;


path = "/Users/dawr2/Desktop/Ranadeep_Daw_Projects/tropomi2";
cd(path);
fls = readdir(path);
df = DataFrame(lons = missing, lats = missing, no2 = missing);
fail_list = [];
for i=1:size(fls,1)
    if last(fls[i],2) == "nc"
        try
            fl = fls[i];
            ds = Dataset(fl);
            ds = ds.group["PRODUCT"];
            lons = ds["longitude"][:][:];
            lats = ds["latitude"][:][:];
            no2  = ds["nitrogendioxide_tropospheric_column"][:][:];
            tmp = DataFrame(lons = lons, lats = lats, no2 = no2);
            df = [df; tmp];
            lons, lats, no2 = nothing, nothing, nothing;
            GC.gc()
            
        catch e
            push!(fail_list,fls[i]);
        end
    end
end

df = df[.!ismissing.(df.no2), :];
ndf = combine(groupby(df, [:lons, :lats]), :no2=> mean, renamecols=false);
#idx = quantile(ndf.no2, 0.025) .< ndf.no2 .< quantile(ndf.no2, 0.975);
#idx = 0 .< ndf.no2 .< quantile(ndf.no2, 0.975);

@save "no2_metadata.jld2" ndf;



idx = quantile(ndf.no2, 0.05) .< ndf.no2 .< quantile(ndf.no2, 0.95);
scatter(ndf.lons[idx, :], ndf.lats[idx, :], zcolor=ndf.no2[idx, :])


ndf2 = ndf[idx, :];
idx2 = sample(1:size(ndf2, 1), 1000);
scatter(ndf2.lons[idx2, :], ndf2.lats[idx2, :], 
        zcolor=ndf2.no2[idx2, :]*10e5,
        markersize=2)
