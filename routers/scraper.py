import time
from fastapi import HTTPException, status, APIRouter
from utilities.scraper_utilities import hospitals_info, cities
from utilities.driver import get_driver

router = APIRouter()


@router.get("/hospitals_data", status_code=status.HTTP_200_OK)
async def get_hospital_data(city: str):
    driver = get_driver()
    if city.title() not in cities:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no hospitals found for the given city, please check your city name and try again.",
        )
    try:
        start = time.time()
        results = hospitals_info(city=city.title(), driver=driver)
        if results and len(results) > 0:
            time_taken = time.time() - start
            return {
                "count": len(results),
                "data": results,
                "time_taken": f"{time_taken:.2f} seconds",
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="no hospitals found for the given city, please check your city name and try again.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error, please try again later.",
        )
    finally:
        driver.quit()
