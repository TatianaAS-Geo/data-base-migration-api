SELECT 
            d.department,
            j.job,
            SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime_str::timestamp) = 1 THEN 1 ELSE 0 END) as Q1,
            SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime_str::timestamp) = 2 THEN 1 ELSE 0 END) as Q2,
            SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime_str::timestamp) = 3 THEN 1 ELSE 0 END) as Q3,
            SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime_str::timestamp) = 4 THEN 1 ELSE 0 END) as Q4
        FROM departments d
        JOIN employees e ON d.id = e.department_id
        JOIN jobs j ON j.id = e.job_id
        WHERE EXTRACT(YEAR FROM e.datetime_str::timestamp) = 2021
        GROUP BY d.department, j.job
        ORDER BY d.department, j.job