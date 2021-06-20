import argparse
import scrape_login as sl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mail", type=str, required=True)
    parser.add_argument("--passwd", type=str, required=True)
    parser.add_argument("--url", type=str, required=True)
    args = parser.parse_args()

    
    c = sl.Collector(mail=args.mail, passwd=args.passwd)
    c.collect_coms(pID=1, link=args.url)
    for row in range(len(c.Comments)):
        reply_link = c.Comments["reply_link"].iloc[row]
        if reply_link != "":
            c.collect_reps(cID=c.Comments["cID"].iloc[row], link=reply_link)
    
    c.Comments.to_csv("comments.csv", index=False)
    c.Replys.to_csv("comments.csv", index=False)


if __name__ == "__main__":
    main()