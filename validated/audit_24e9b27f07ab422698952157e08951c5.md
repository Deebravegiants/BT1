### Title
Webhook Shop Attribution Not Covered by HMAC Signature Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain` (and `topic`, `webhook-id`, `api-version`) HTTP headers — none of which are covered by that HMAC — to attribute the payload to a specific merchant before invoking the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw JSON body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated headers with no coverage by the signed content: [2](#0-1) 

`Registry.process` validates only this body HMAC before dispatching to the handler with `request.shop` used as the tenant identifier: [3](#0-2) 

The HMAC secret (`Context.api_secret_key`) is the app's shared `client_secret` — identical for every merchant shop that has installed the app, not a per-shop secret: [4](#0-3) 

The identity binding the gem is supposed to enforce is: *the shop that produced/authorized a given webhook body* == *the shop the application attributes that body to*. Because only the body bytes are HMAC-verified, and the `shop-domain` header is not part of the signed content, that equality is never checked. Anyone who can obtain one genuine `(body, hmac)` pair for the app (e.g., by triggering a webhook on their own installed shop, or via network/log exposure of a delivered webhook) can resubmit the same body/HMAC to the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header. `Utils::HmacValidator.validate` will still return `true` (the body and secret are unchanged), and `Registry.process` will hand the payload to the handler tagged with the attacker-chosen shop.

### Impact Explanation
This crosses a tenant boundary: data legitimately generated for/by shop A can be injected into the application's processing pipeline as if it belonged to shop B, since the shop attribution is taken from a field the gem's own signature check does not cover. Depending on how the host app persists webhook data keyed by `shop`, this can lead to cross-tenant data corruption or disclosure — matching the "cross-tenant access" high-impact category, achieved purely through this gem's `Webhooks::Request`/`Registry` verification logic without needing the victim's access token or `client_secret`.

### Likelihood Explanation
Exploitation requires only one valid `(raw_body, hmac)` pair for the target app, which is trivially obtainable by any developer/merchant who has installed the app (they receive real webhooks with valid HMACs signed by the same shared `api_secret_key`) or by anyone who can observe a delivered webhook in transit/logs. No access token, `client_secret`, or privileged account is needed — the attacker only replays a captured request to the app's public webhook endpoint with a modified header, which this gem's `Registry.process`/`Request` classes accept as valid because header integrity is never checked.

### Recommendation
Bind the `shop`, `topic`, `webhook_id`, and `api_version` header values into the signable content used for HMAC validation (or otherwise cryptographically bind them to the body), so that any header tampering invalidates the HMAC check. At minimum, `Request#to_signable_string` should incorporate the shop domain, and `HmacValidator` should be updated so header spoofing cannot pass validation for a payload signed for a different shop/topic.

### Proof of Concept
1. App installs on `victim-shop.myshopify.com` and `attacker-shop.myshopify.com` (same app, same shared `api_secret_key`).
2. Attacker triggers/observes a legitimate webhook delivered to the app for `attacker-shop.myshopify.com`, capturing `raw_body` and the valid `x-shopify-hmac-sha256` value.
3. Attacker POSTs the same `raw_body` and `hmac-sha256` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers; `Utils::HmacValidator.validate` succeeds because it only rehashes `@raw_body` against `Context.api_secret_key`, per [5](#0-4)  and [6](#0-5) .
5. `Registry.process` invokes the handler with `shop: request.shop` == `"victim-shop.myshopify.com"`, causing the attacker-controlled body to be attributed to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
