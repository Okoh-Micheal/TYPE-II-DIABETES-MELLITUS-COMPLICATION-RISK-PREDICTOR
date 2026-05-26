-- COMPLICATION PROFILE OF ENTIRE POPULATION --1

SELECT 
	COUNT(*) AS All_patients,   
    -- Here, I calculate the percentage of patients with complications
    ROUND(AVG("Target_Complication_Flag") * 100, 1) || '%' AS complication_rate,
    
    -- I would like to know the glycated hemoglobin, HbA1C_mmol and years since diagnosis
    ROUND(AVG("HbA1c_mmol"), 2) AS avg_hba1c,
    ROUND(AVG("Diabetes_Duration_Years"), 1) AS avg_diabetes_duration 
FROM "T2DM" ;

-- 18.6% of the population has complications from type 2 diabetes mellitus.
-- The average blood sugar concentration of the population is 60.34mmol
-- The average years of diabetes diagnosis is 8


-- 2
-- COMPLICATION RISK ACROSS AGE GROUPS
-- I bin patients into various age brackets
-- and show complication rate per group as a bar chart. 
-- This matters because age cannot be modified. 
-- A clinician needs to know which age cohort to watch most closely so they can allocate screening resources accordingly.

SELECT
    CASE 
        WHEN "Age" BETWEEN 30 AND 45 THEN '30–45'
        WHEN "Age" BETWEEN 46 AND 60 THEN '46–60'
        WHEN "Age" BETWEEN 61 AND 75 THEN '61–75'
        WHEN "Age" > 75 THEN '75+'
    END AS age_bracket,
    COUNT(*) AS patient_count,
    ROUND(AVG("Target_Complication_Flag") * 100, 1) || '%' AS complication_rate
FROM "T2DM"
GROUP BY 1
ORDER BY MIN("Age");

-- As expected, older patients have a higher rate of complications.
-- The older the patient, the higher the risk of complication.




--3
--IS GLYCATED HEMOGLOBIN THE MAJOR DRIVER OF COMPLICATIONS? -- 
-- I bin the glycated hemoglobin into clinical ranges — below 48 (target range), 48–64 (above target), above 64 (high risk) — and show complication rates per band. 
--This is the single most clinically important chart in the dashboard.

SELECT
	CASE 
		WHEN "HbA1c_mmol" < 48 THEN 'Target Range'
		WHEN "HbA1c_mmol" BETWEEN 48 AND 64 THEN 'Above Target'
		WHEN "HbA1c_mmol" > 64 THEN 'High Risk'
	END AS Blood_Sugar_Level,
COUNT(*) AS patient_count,
ROUND(AVG("Target_Complication_Flag") * 100, 1) || '%' AS complication_rate
FROM "T2DM"
GROUP BY 1
ORDER BY AVG("Target_Complication_Flag") DESC;


-- As we clearly see the data, those with higher levels of glycated hemoglobin have a
-- higher complication rate than those within the target range.



--4
-- Does smoking status compound risk beyond what HbA1c alone explains?
--A grouped bar chart: complication rate by smoking status, broken down by HbA1c band.
--This tests whether smoking adds independent risk on top of poor glycaemic control. The answer from your dissertation data is yes — and showing that interaction visually is genuinely useful for a population health team designing intervention priorities.
SELECT
			CASE 
		WHEN "HbA1c_mmol" < 48 THEN 'Target Range'
		WHEN "HbA1c_mmol" BETWEEN 48 AND 64 THEN 'Above Target'
		WHEN "HbA1c_mmol" > 64 THEN 'High Risk'
	END AS Blood_Sugar_Level,
		"Smoking_Status",
		ROUND((AVG("Target_Complication_Flag") * 100), 1) as complication_rate
FROM "T2DM"
GROUP BY 1,2
ORDER BY 2,1

-- Smoking actually compounds complication rate beyond what glycated hemoglobin
-- A current smoker is more likely to have complications than an ex smoker or non smoker, except
-- the ex-smoker or non - smoker already has high levels of glycated hemoglobin




--5
-- Which patient segment is highest risk — and how large is it?
-- Combine HbA1c above 64, diabetes duration above 10 years, and 
-- current smoker status to define a "triple risk" cohort.
-- How many patients fall into it? What is their complication rate?
--This is population segmentation letting us know exactly which patients need urgent intensive management.

SELECT 
    CASE 
        WHEN "HbA1c_mmol" > 64 
             AND "Diabetes_Duration_Years" > 10 
             AND "Smoking_Status" = 'Current Smoker'
        THEN 'Triple Risk Cohort'
        ELSE 'Other Patients'
    END AS risk_segment,
    COUNT(*) AS patient_count,
    ROUND(AVG("Target_Complication_Flag") * 100, 1) || '%' AS complication_rate
FROM "T2DM"
GROUP BY 1;

-- 205 of the all patients have a 63.9% risk of being in the Triple Risk Cohort ie 
-- High glycated hemoglobin, over 10 years of diagnosis and are current smokers
-- The Triple Risk Cohort has the highest risk, but thats just about 2% of the population.



--6
--  Are there ethnic disparities in complication rates?
-- Break complication rate by ethnicity.
-- This is sensitive but clinically important as the NHS has documented that South Asian and Black patients face elevated T2DM complication risk.
-- I expect the disparity should show up.

SELECT "Ethnicity",
ROUND(AVG("Target_Complication_Flag") * 100, 1) as complication_rate
FROM "T2DM"
GROUP BY  1
ORDER BY 2 DESC

--black and Asian patients have a higher risk of complication.



--7. How does diabetes duration relate to risk — and does it interact with age?
-- A scatter plot or binned line chart: average complication rate by years since diagnosis, with age as a colour layer.
-- This visualises the "legacy effect" you identified in your dissertation 
-- the longer someone has diabetes, the higher the cumulative damage regardless of how well it's currently controlled. 
-- Powerful for making the case for early diagnosis programmes.

SELECT 
    -- 1. Age Segmentation
    CASE 
        WHEN "Age" < 50 THEN 'Younger (<50)'
        ELSE 'Older (50+)'
    END AS age_cohort,
    
    -- 2. Duration Segmentation
    CASE 
        WHEN "Diabetes_Duration_Years" < 10 THEN 'Short (<10yrs)'
        WHEN "Diabetes_Duration_Years" BETWEEN 10 AND 20 THEN 'Medium (10-20yrs)'
        ELSE 'Long (20yrs+)'
    END AS duration_cohort,
    
    -- 3. Metrics
    COUNT(*) AS total_patients,
    ROUND(AVG("Target_Complication_Flag") * 100, 1) || '%' AS complication_rate
FROM "T2DM"
GROUP BY 1, 2
ORDER BY 1 DESC, MIN("Diabetes_Duration_Years") ASC;

-- Patients who have been diagnosed the longest seem to have higher risk of complications
-- The age does not really matter- the years since diagnosis count more.




-- 8. What does the risk distribution across the full population look like?
-- Use Risk_Probability_True — the continuous score — to show a histogram of predicted risk across all 10,000 patients. 
-- Overlay the 30%, 70% thresholds to show the Low / Moderate / High triage segments. 
-- This connects your Power BI dashboard directly to the Streamlit ML app. Same data, two different tools, one coherent story.
-- That continuity across your portfolio is what makes it look professional rather than a collection of random projects.

SELECT "Patient_ID", "Risk_Probability_True"
FROM "T2DM"

SELECT 
    -- This rounds the probability to one decimal place (e.g., 0.1, 0.2)
    ROUND("Risk_Probability_True", 1) AS risk_bucket,
    -- This shows the actual count of patients in that bucket
    COUNT(*) AS patient_count
    -- This creates a simple text-based bar chart using the REPEAT function
  --  RPAD('', COUNT(*)/50, '█') AS visual_distribution
FROM "T2DM"
GROUP BY 1
ORDER BY 1;


