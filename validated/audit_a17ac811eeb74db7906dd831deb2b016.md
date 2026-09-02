## Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook impersonation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw request body only. The `shop-domain` (and `topic`, `webhook-id`, `api-version`) headers, which are used to identify which merchant/tenant the event belongs to, are read directly from unauthenticated HTTP headers and are never included in the signed payload. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` when constructing the `WebhookMetadata` passed to the host app's handler, after only checking that the HMAC over the body validates. This breaks the binding "shop authenticated by HMAC == shop acted upon by the handler."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `api_version`, and `webhook_id` are parsed straight from headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`HmacValidator.validate` only checks that the received HMAC matches `HMAC(secret, raw_body)`: [3](#0-2) 

`Registry.process` performs exactly that check, then immediately builds the `WebhookMetadata` from `request.shop`, `request.topic`, etc., all of which came from the unauthenticated headers: [4](#0-3) 

Because the signature is a keyed HMAC over the body alone, any `(raw_body, hmac)` pair that is valid for one webhook delivery remains valid for that same body regardless of which `shop-domain`/`topic` header accompanies it. A merchant who owns their own development/test store can subscribe to a webhook topic on their own shop, capture a legitimate `(body, hmac)` pair produced by Shopify for a real event on their own store, and then submit that same body+hmac to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and/or `x-shopify-topic`) header. The gem will validate the HMAC successfully (it only checks the body) and will hand the handler a `WebhookMetadata` claiming the event is `shop: <victim-shop>`.

### Impact Explanation
This is a cross-tenant identity-binding break: the value the gem certifies as authentic (the HMAC-verified body) is disjoint from the value the host application uses to select which tenant's data to act on (`request.shop`, taken from an unauthenticated header). Depending on which webhook topic the attacker replays, this can be leveraged to make the app believe another shop uninstalled the app, requested data redaction, or emitted some other topic-triggered side effect, causing the app to act against the wrong merchant's session/data — a cross-tenant access/integrity violation attributable to this gem's own webhook-verification code, not to host application misuse.

### Likelihood Explanation
Exploitation only requires the attacker to control one shop that installs the target app and subscribes to any webhook topic (trivial for any developer/attacker who can install a free/dev Shopify app), plus the ability to send arbitrary HTTP requests to the app's public webhook endpoint (which is Internet-reachable by design). No access token, `client_secret`, or privileged account is required — the attacker never needs Shopify's real secret, only a replayable valid signature/body pair from their own tenant.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, and ideally `webhook-id`) in the signed material that `HmacValidator` checks, or otherwise cryptographically bind them to the request (e.g., verify them against Shopify's per-request signature scheme rather than trusting raw headers). At minimum, `Registry.process` should not treat `request.shop`/`request.topic` as authenticated data unless they are proven to correspond to the same delivery whose body produced the valid HMAC.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and registers a webhook for topic `app/uninstalled` (or any sensitive topic).
2. Shopify delivers a legitimate webhook to the app's endpoint:
   - headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: app/uninstalled`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`
   - body: `{...}` (whatever Shopify sends)
3. Attacker replays the exact same body and `x-shopify-hmac-sha256` value to the same endpoint but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(secret, raw_body)` — see: [5](#0-4) 
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(topic: "app/uninstalled", shop: "victim-shop.myshopify.com", ...)`, causing the host app to act as though the victim shop triggered the event.

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
