# Start with the official MySQL 8 image
FROM mysql:8

# Copy your custom my.cnf file to the correct directory in the container
COPY ./db/my.cnf /etc/mysql/my.cnf

# Set the correct permissions on the my.cnf file (644) to avoid MySQL ignoring it
RUN chmod 644 /etc/mysql/my.cnf

# Set the correct ownership for the my.cnf file (usually root)
RUN chown root:root /etc/mysql/my.cnf
