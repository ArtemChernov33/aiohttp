from asyncio import run

import aiohttp


async def main():

    async with aiohttp.ClientSession() as session:
        # response = await session.post('http://127.0.0.1:8080/mails/', json={'header':'notification2', 'description':'You must submit on time HW'})
        # print(await response.json())
        # response = await session.get("http://127.0.0.1:8080/mails/1")
        # print(await response.json())
        # response = await session.delete("http://127.0.0.1:8080/mails/3")
        # print(await response.json())
        # response = await session.patch('http://127.0.0.1:8080/mails/1', json={'header':'notification123', 'description':'You must submit on time HW'})
        # print(await response.json())
        response = await session.get("http://127.0.0.1:8080/mails/1")
        print(await response.text())
run(main())

# HOST = 'http://127.0.0.1:5000'

# response = requests.get(HOST)
# print(response.status_code)
# print(response.text)


# response = requests.post(f'{HOST}/mails/', json={'header':'notification2', 'description':'You must submit on time HW', 'sender':'Prepod'})
# print(response.status_code)
# print(response.text)


# response = requests.patch(f'{HOST}/mails/1', json={'header':'notification_2'})
# print(response.status_code)
# print(response.text)

# response = requests.delete(f'{HOST}/mails/1')
# print(response.status_code)
# print(response.text)

# response = requests.get(f'{HOST}/mails/2')
# print(response.status_code)
# print(response.text)