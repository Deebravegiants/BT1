## Title
Webhook Shop/Topic Identity Spoofing via Header Fields Not Covered by HMAC - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the attacker-suppliable `shop-domain`, `topic`, `webhook-id`, and `api-version` HTTP headers to the app's handler as trusted identity metadata. Because those headers are never included in the HMAC-signed content, any party who has legitimately obtained one valid `(raw_body, hmac)` pair (e.g. from a webhook delivered to their own store) can freely rewrite the `shop-domain` header to any victim shop and the signature will still validate, letting them impersonate webhook traffic "from" a different tenant.

### Finding Description
`Utils::HmacValidator.validate` computes the signature from `verifiable_query.to_signable_string`, and for webhooks that method returns only `@raw_body`: [1](#0-0) [2](#0-1) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all pulled directly from unauthenticated headers, with no involvement in the signable string: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever compares the HMAC against `to_signable_string` (i.e., the body), never the headers: [4](#0-3) 

`Registry.process` treats a passing HMAC check as authorization to trust `request.shop`, `request.topic`, and `request.webhook_id` and dispatches them straight to the app-provided handler as `WebhookMetadata`: [5](#0-4) 

The identity binding the library implicitly promises to the host application is:
`hmac_valid(raw_body) == true` ⟹ `shop header == the shop that actually generated raw_body`

That equality does not hold: the HMAC only proves "Shopify's API secret was used to sign this exact `raw_body`" — it says nothing about which shop the body came from. Any actor who can obtain one legitimate `(raw_body, hmac)` pair (trivial: install the app on a store they control, or capture any webhook delivery for any shop) can replay that exact body+hmac to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` will still return `true` because it never looks at the shop header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the spoofed shop.

### Impact Explanation
Apps built on this gem are documented to use `WebhookMetadata#shop` to determine which merchant's data record to create/update/delete (per `docs/usage/webhooks.md`'s stated usage pattern). Because the shop identity is not cryptographically bound to the payload, this allows cross-tenant data injection/corruption: an attacker-controlled or externally captured webhook body can be attributed to a victim shop of the attacker's choosing, achieving cross-tenant access/write into another merchant's data path without ever possessing that merchant's credentials.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint and one legitimately-signed `(raw_body, hmac)` pair, which is trivially obtainable by any developer who installs the target app on their own (attacker-controlled) development store — no access token, `api_secret_key`, or victim credentials are needed. This is a realistic, low-effort "unprivileged internet user" attack path.

### Recommendation
Bind the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) into the value that is HMAC-verified — or at minimum have `Registry.process`/the handler cross-check `request.shop` against the shop the app expects to receive that `topic`/`webhook_id` for (e.g., verify the webhook was actually registered for that shop via a lookup) before trusting it as an identity claim. Document clearly that only `raw_body` is authenticated and headers must not be treated as verified identity data without additional binding.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and receives a legitimate webhook delivery, capturing the exact `raw_body` and the `x-shopify-hmac-sha256` header Shopify sent.
2. Attacker sends a POST to the app's webhook endpoint with the same `raw_body` and the same (still-valid) HMAC header, but sets `x-shopify-shop-domain: victim.myshopify.com` (and optionally a topic value already registered by the app for that store).
3. `Utils::HmacValidator.validate` recomputes the signature over `raw_body` only, matches the replayed HMAC, and returns `true`.
4. `Registry.process` proceeds to call the app's handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)`, causing the application to process/store attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
