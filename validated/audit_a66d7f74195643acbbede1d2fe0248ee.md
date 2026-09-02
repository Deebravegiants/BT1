### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by HMAC-verifying only the raw request body, then trusts the unauthenticated `shop-domain` (and `topic`) headers to build the `WebhookMetadata` passed to the host app's handler. Since the shop identity is never part of the signed payload, an attacker who can obtain any single valid `(raw_body, hmac)` pair for the app (e.g. from their own legitimate webhook deliveries, since they control their own shop and thus receive their own valid webhooks) can replay that exact body/HMAC pair while substituting the `shopify-shop-domain` header to name a different (victim) shop. `HmacValidator.validate` still passes because it only checks the body against the secret, never binding the shop field into the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, whose contract is `hmac` and `to_signable_string`. [1](#0-0) 

`Request#to_signable_string` returns only `@raw_body` — none of the headers (topic, shop-domain, api-version, webhook-id) are included in the signed material: [2](#0-1) 

`HmacValidator.validate`/`validate_signature` computes the HMAC purely over `verifiable_query.to_signable_string` (i.e. the raw body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` uses this same unauthenticated `request.shop` (and `request.topic`) value to build the `WebhookMetadata` struct that is handed directly to the app's `WebhookHandler#handle`: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `shop field trusted by handler == shop field cryptographically covered by the HMAC`. In this implementation that equality does not hold — `shop` (and `topic`) are read straight from headers with `shopify_header("shop-domain")`/`shopify_header("topic")` and are never mixed into `to_signable_string`: [6](#0-5) [7](#0-6) 

This is the same bug class as the external report: an action (here, attributing a webhook payload/topic to a specific shop/tenant) is taken on the strength of an unsigned identity field, while only a separate signature (here, over the body alone) is actually verified.

### Impact Explanation
In a multi-tenant app that installs this gem for many merchant shops, any merchant who is a legitimate tenant (an "unprivileged internet user" relative to other tenants — they have no elevated access, no `api_secret_key`, no other shop's credentials) receives their own genuinely-signed webhooks from Shopify. Because the HMAC covers only the body, that same `(raw_body, hmac)` pair remains valid for **any** `shop-domain` value the attacker chooses to send to the app's webhook endpoint. By replaying their own valid webhook body while spoofing the `shopify-shop-domain` header to a victim shop, the attacker can make the host application process attacker-controlled webhook content under another tenant's identity. Depending on the handler's logic (e.g., updating orders/inventory/customer records keyed by `data.shop`), this results in cross-tenant data confusion/corruption — data intended for or attributed to shop A gets applied against shop B's records purely because the gem exposes an unauthenticated `shop` field as if it were verified.

### Likelihood Explanation
Likelihood is moderate to high in any multi-tenant deployment: the attacker only needs to be one of the app's own installed merchants (no secret leakage, no privileged access, no social engineering) — they naturally receive valid `(body, hmac)` pairs for topics they can trigger on their own store (e.g. `orders/create` by placing an order), and can then POST that identical body/HMAC to the app's public webhook endpoint with a different `shop-domain` header. The gem never rejects this because the header is outside the signed scope.

### Recommendation
Bind the shop (and ideally topic) identity into the value that is cryptographically verified rather than trusting the header value as-is:
- Cross-check `request.shop` against the shop associated with the session/subscription that would legitimately receive this specific `webhook_id`/topic combination before invoking the handler, or
- If Shopify's wire format cannot be changed, at minimum require the host application to validate `data.shop` against its own known set of shops for that specific webhook subscription id server-side, and document this gap explicitly, since the gem cannot itself strengthen Shopify's signature format.

### Proof of Concept
1. App is installed for `shop-a.myshopify.com` (attacker's own store) and `shop-b.myshopify.com` (victim).
2. Attacker triggers a real event (e.g. creates an order) on `shop-a`, and Shopify sends a legitimately signed webhook: headers `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, body `B`.
3. Attacker replays this exact request to the app's public webhook endpoint, but rewrites `x-shopify-shop-domain` to `shop-b.myshopify.com`, keeping body `B` and the same `x-shopify-hmac-sha256` value.
4. `Utils::HmacValidator.validate` in `hmac_validator.rb` recomputes the HMAC over body `B` only, which still matches, so `Registry.process` (`registry.rb:188-200`) proceeds and calls the app's handler with `WebhookMetadata.new(shop: "shop-b.myshopify.com", ..., body: B)` — attacker-controlled data now processed under the victim shop's identity, without ever knowing `shop-b`'s credentials.

### Citations

**File:** lib/shopify_api/utils/verifiable_query.rb (L10-16)
```ruby

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L66-70)
```ruby

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
