### Title
Webhook `shop` tenant identifier is read from an unauthenticated header and is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#shop` derives the tenant identifier straight from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` HTTP header, while `Request#to_signable_string` — the data actually covered by the HMAC check in `Utils::HmacValidator.validate` — is only the raw request body. The `shop` value is then forwarded, unverified, into `WebhookMetadata` and dispatched to the host application's handler as the tenant key.

### Finding Description
`HmacValidator.validate` computes and compares the HMAC over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

But the tenant-identifying `shop` accessor reads directly from the `shopify-shop-domain` header, which is not part of the signed bytes: [3](#0-2) 

`Registry.process` validates the HMAC over the request (i.e., only the body), then immediately trusts `request.shop` — taken from the unauthenticated header — as the tenant key passed into the handler's `WebhookMetadata`: [4](#0-3) 

This breaks the intended binding: `shop == bytes_actually_authenticated_by_HMAC`. In reality, the HMAC only proves "these body bytes were produced with the app's `client_secret`"; it proves nothing about which shop the header claims to represent, since the header is fully attacker-controllable and outside the signed payload — an exact match to the "bytes verified vs. bytes parsed" / "shop authenticated vs. shop used as identity key" pattern highlighted in the bug-class hint (invalid/unbound signature check leading to a mismatch between what is cryptographically verified and what is trusted downstream).

### Impact Explanation
In a multi-tenant host application (the common integration pattern for this gem — one endpoint, one `client_secret`, many installed shops), a malicious merchant with a legitimate installation of the app can capture a genuine webhook delivery Shopify sends them (valid `raw_body` + valid HMAC, since Shopify computes the HMAC purely from body + the app's shared secret, independent of which shop it's for). They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header for a different victim shop. `HmacValidator.validate` still passes (body/HMAC unchanged), but `Registry.process` hands the handler a `WebhookMetadata` claiming the payload belongs to the victim shop. Any host logic that uses `WebhookMetadata#shop` to select which tenant's session/data store to write into (e.g., updating orders, redacting customer data for `shop/redact`/`customers/redact`/`customers/data_request`, or feeding tenant-scoped business logic) can be tricked into acting on/for the wrong tenant — a cross-tenant data-integrity and confidentiality break driven purely by unprivileged internet-facing webhook traffic, without needing the `client_secret`, an access token, or any privileged account.

### Likelihood Explanation
Any merchant who installs the app receives real webhook traffic addressed to their own shop, giving them a valid `(body, hmac)` pair signed by the real `client_secret` at no cost. Replaying it with a modified shop-domain header requires only a normal HTTP client — no cryptographic material, no social engineering, no TLS interception. The only work required is finding/waiting for a webhook whose body content is useful for the target shop (or one of the mandatory GDPR topics `shop/redact` / `customers/redact` / `customers/data_request`, which take no shop-specific payload data at all and are trivially replayable across shops).

### Recommendation
Bind the trusted `shop` value to data that is actually covered by the HMAC, or otherwise cryptographically/authoritatively re-derive it instead of trusting the header in isolation:
- Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed payload check, e.g., validate `hmac(secret, raw_body + shop_domain_header)` against an expected signature computed the same way, or
- Cross-check `request.shop` against an independently obtained, trusted mapping (e.g., look up the shop's own registered/stored session record and access token rather than trusting the header value verbatim as the record key), so a replayed body cannot be reattributed to a different tenant purely by changing a header.

### Proof of Concept
1. App is installed by Shop A (attacker-controlled) and Shop B (victim), sharing one `client_secret` and one webhook endpoint.
2. Shopify delivers a webhook to the app for Shop A:
   - Headers: `X-Shopify-Shop-Domain: shop-a.myshopify.com`, `X-Shopify-Hmac-SHA256: <valid-hmac-of-body>`
   - Body: `{"id": 123, ...}`
3. Attacker (Shop A's owner) captures this request and replays it to the same endpoint, only changing the header:
   - `X-Shopify-Shop-Domain: shop-b.myshopify.com`
   - Same body and same `X-Shopify-Hmac-SHA256` (unchanged, still valid because HMAC only covers the body).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — passes, because `to_signable_string` only checked the body. [5](#0-4) 
5. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` is invoked with `shop == "shop-b.myshopify.com"`, even though the payload actually originated for Shop A. [6](#0-5) 
6. Any host-side handler logic keyed on `data.shop` now operates on Shop B's tenant context using Shop A's forged/replayed payload.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
