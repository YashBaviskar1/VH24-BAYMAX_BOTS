import requests

def lookup_asn_by_ip(ip_address):
    url = f"https://stat.ripe.net/data/prefix-overview/data.json"
    params = {"resource": ip_address}
    response = requests.get(url, params=params)
    process_response(response, ip_address)

def fetch_asn_neighbors(asn):
    url = f"https://stat.ripe.net/data/asn-neighbours/data.json"
    params = {"resource": asn}
    response = requests.get(url, params=params)
    process_response(response, asn, neighbor=True)

def fetch_asn_neighbors_history(asn):
    url = f"https://stat.ripe.net/data/asn-neighbours-history/data.json"
    params = {"resource": asn}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        neighbours = data['data'].get('neighbours', [])
        if neighbours:
            print(f"Historical neighbor ASNs for ASN {asn}:")
            for neighbour in neighbours:
                asn = neighbour.get('neighbour')
                timelines = neighbour.get('timelines', [])
                print(f"ASN: {asn}, Timelines:")
                for timeline in timelines:
                    starttime = timeline.get('starttime', 'Start time not found')
                    endtime = timeline.get('endtime', 'End time not found')
                    print(f"    Start: {starttime}, End: {endtime}")
        else:
            print(f"No historical neighbor information found for ASN {asn}")
    else:
        print("Failed to retrieve data. Status code:", response.status_code)

def process_response(response, resource, neighbor=False, history=False):
    if response.status_code == 200:
        data = response.json()
        if neighbor or history:  # Assuming similar handling for both cases
            neighbors = data['data']['neighbours']
            print(f"Neighbors for ASN {resource}:")
            for neighbor in neighbors:
                asn = neighbor.get('asn', 'ASN not found')
                type_ = neighbor.get('type', 'Type not found')
                power = neighbor.get('power', 'Power not found')
                v4_peers = neighbor.get('v4_peers', 'IPv4 Peers not found')
                v6_peers = neighbor.get('v6_peers', 'IPv6 Peers not found')
                print(f"ASN: {asn}, Type: {type_}, Power: {power}, IPv4 Peers: {v4_peers}, IPv6 Peers: {v6_peers}")
        else:
            asns = data['data'].get('asns', [])
            if asns:
                print(f"IP Address {resource} is associated with the following ASN(s) and holder(s):")
                for asn_info in asns:
                    asn = asn_info.get('asn', 'ASN not found')
                    holder = asn_info.get('holder', 'Holder not found')
                    print(f"ASN: {asn}, Holder: {holder}")
            else:
                print(f"No information found for {resource}")
    else:
        print(f"Failed to retrieve data for {resource}. Status code: {response.status_code}")

def main():
    print("Choose an option:")
    print("1. Look up ASN and organization name by IP address")
    print("2. Fetch neighbor ASNs for a given ASN")
    print("3. Fetch historical neighbor ASNs for a given ASN")
    
    choice = input("Enter your choice (1, 2, or 3): ")

    if choice == '1':
        ip_address = input("Enter an IP address to look up: ")
        lookup_asn_by_ip(ip_address)
    elif choice == '2':
        asn = input("Enter an ASN to find its neighbors: ")
        fetch_asn_neighbors(asn)
    elif choice == '3':
        asn = input("Enter an ASN to find its historical neighbors: ")
        fetch_asn_neighbors_history(asn)
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()