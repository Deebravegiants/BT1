### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` value from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, but the HMAC signature used to authenticate the webhook only covers the raw request body. This breaks the identity binding `bytes verified == bytes acted on`: the `shop` field is acted on (passed to the handler as the authoritative tenant identity) but is not included in the HMAC-verified data.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Registry.process` validates the webhook exclusively via `Utils::HmacValidator.validate(request)`, which calls `to_signable_string` (i.e. only the raw body) against the app's secret: [2](#0-1) [3](#0-2) 

After the HMAC check passes, `request.shop` — read straight from the unauthenticated `shopify-shop-domain` header — is forwarded as the trusted tenant identifier into the handler: [4](#0-3) [5](#0-4) 

Because `shop-domain` is never part of the signed payload, an attacker who can obtain any single valid `(raw_body, hmac)` pair for the app — e.g. by installing the app on a store they control and capturing one of their own legitimately-triggered webhooks — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary value for the `shopify-shop-domain` header. `HmacValidator.validate` will still succeed (it only checks the body bytes), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event originated from a shop the attacker does not control.

This is exactly the class of bug described in the reference report: a field that is acted upon (here, the tenant/shop attribution used by the host application to route webhook data, e.g. loading that shop's session or writing to that shop's records) is not covered by the same cryptographic check (HMAC) that is otherwise used to authenticate the request.

### Impact Explanation
This allows cross-tenant confusion: a malicious but otherwise unprivileged app-installer (a real merchant with legitimate low-privilege access to trigger webhooks for their own shop) can forge webhook events that are processed by the host application as if they belong to a different, victim shop. Any application logic keyed off `WebhookMetadata#shop` (session lookup, data attribution, redaction/GDPR handling, billing, etc.) can be manipulated to act on the wrong tenant, i.e. cross-tenant access — a Critical-class impact per the given rules.

### Likelihood Explanation
Exploitability requires only the ability to trigger one webhook for a shop the attacker legitimately controls (trivial for any app-installing merchant) and the ability to send an HTTP POST with a modified header to the app's webhook endpoint, replaying the same body/HMAC. No access token, `api_secret_key`, or privileged account is required, matching the "unprivileged internet user" threat model.

### Recommendation
Include the shop domain (and topic/webhook-id, if used for routing/dedup decisions) in the HMAC-signed material, or otherwise cryptographically bind the header-derived `shop` value to the signed body (e.g., by validating it against Shopify's known registered shop for the given HMAC/secret, or requiring the app to independently confirm the shop via an authenticated channel) before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers any webhook topic handled by the app, capturing the raw POST body and the `x-shopify-hmac-sha256` header sent by Shopify.
2. Attacker resends the identical raw body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` (in `lib/shopify_api/utils/hmac_validator.rb`) recomputes the HMAC over `request.to_signable_string` (the raw body only) and it matches, so validation succeeds.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the host application to process attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

### Citations

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
