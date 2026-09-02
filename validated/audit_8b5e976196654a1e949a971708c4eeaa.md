### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity by computing an HMAC over the raw request body only, then trusts the unauthenticated `X-Shopify-Shop-Domain` header as the tenant identity passed to the host application's handler. Because the shop-domain field is not part of the signed data, a party who possesses one valid `(body, hmac)` pair for the app (e.g. a malicious merchant who has installed the app and received a legitimately signed webhook for their own store) can replay that exact body/hmac pair while substituting the shop-domain header for a victim shop. The signature check still passes, and the handler is invoked believing the payload originated from the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not included in the signable string at all: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)` — which computes `HMAC-SHA256(api_secret_key, request.to_signable_string)` and compares it to the header-supplied HMAC — and, once that check passes, hands the *header-derived* `request.shop` straight to the registered handler: [3](#0-2) 

`Utils::HmacValidator.validate` only ever verifies `verifiable_query.to_signable_string` against the secret — it has no way to bind the `shop` header, since `Request#to_signable_string` never includes it: [4](#0-3) 

This is the same class of bug as the report: a field that is *acted on* (here, the tenant-identifying `shop` passed into `WebhookMetadata` and used by the host app to attribute the webhook) is not covered by the cryptographic check that is supposed to authenticate the request. The equality that should hold — `shop authenticated by HMAC == shop the handler processes as` — is broken because the HMAC is computed over `raw_body` alone, and `shop` is sourced from a header outside that signed scope.

Because Shopify's webhook HMAC secret (`Context.api_secret_key`, the app's client secret) is shared across **all** shops that have installed the app, any single shop that installs the app can obtain a valid `(body, hmac)` pair for its own webhook traffic. That shop can then resend the same body+hmac to the app's webhook receiver with the `shop-domain` header rewritten to any other installed shop. `HmacValidator.validate` still returns `true` (the body/hmac pair is valid), so `Registry.process` calls `handler.handle` with `WebhookMetadata#shop` set to the victim's domain and `body` set to attacker-controlled JSON.

### Impact Explanation
If the host application's webhook handler uses `WebhookMetadata#shop` to look up the victim's stored session/access token and applies `WebhookMetadata#body` against that tenant's data (a documented, expected usage pattern per `WebhookHandler#handle`), this yields cross-tenant data injection/corruption: one merchant can cause another merchant's app-side records to be updated using data of the attacker's choosing, without ever compromising the victim's credentials. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only installing the app as a normal, unprivileged merchant (or otherwise obtaining one legitimately signed webhook delivery) — no `api_secret_key`, no stolen credentials, no TLS interception, and no social engineering are required. The only work needed is resending an HTTP POST with a different `X-Shopify-Shop-Domain`/`shopify-shop-domain` header, which any caller of the app's public webhook endpoint can do.

### Recommendation
Bind the tenant identity into the authenticated payload. Options:
- Include the shop-domain header in the HMAC-signed data (`to_signable_string`), or
- Independently verify that `request.shop` corresponds to a shop with a currently stored, valid session/access token for this app before trusting it as the tenant context, or
- Reject/ignore any webhook whose `shop` cannot be cryptographically tied to the same request the signature was computed over.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com` and trigger any webhook subscribed via `Registry`/`Registrations::Http` (e.g. `orders/create`). Capture the raw POST: headers including `X-Shopify-Hmac-Sha256: <hmac>` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, plus the JSON body.
2. Resend the identical request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (leave body and HMAC header untouched).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (the unchanged raw body) and matches the supplied HMAC — validation succeeds.
4. `handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...))` is invoked, and the host app's handler processes attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
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
