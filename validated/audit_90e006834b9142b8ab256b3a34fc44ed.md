### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the webhook HMAC over the raw request body only, while the `shop` (tenant identifier), `topic`, `api_version`, and `webhook_id` are taken verbatim from unauthenticated HTTP headers and passed straight through to the app's handler as trusted metadata. An attacker who controls a legitimately-signed webhook body/HMAC pair (e.g. one delivered to their own store) can replay it with a forged `shop-domain` header, and the gem will report it as HMAC-valid for the attacker-chosen shop.

### Finding Description
`Request#hmac` and `Request#to_signable_string` bind the HMAC only to `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all read directly from HTTP headers that are not part of the signed payload: [2](#0-1) 

`Registry.process` validates only the HMAC via `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e. only the body) against `verifiable_query.hmac` (the `hmac-sha256` header): [3](#0-2) [4](#0-3) 

After this single check passes, the unauthenticated `request.shop` header value is forwarded as trusted tenant identity into `WebhookMetadata`, which the host app's `WebhookHandler#handle` uses to key its per-shop logic (e.g. look up a session/store record by shop domain and act on the body as if it originated from that shop): [5](#0-4) [6](#0-5) 

The binding that should hold is: `shop-domain header == shop that produced the HMAC over (body, shop, topic)`. Instead the gem only proves `hmac == HMAC(secret, body)`, and trusts `shop-domain` unconditionally. Since `secret` (the app's `api_secret_key`) is fixed across all shops installing the app, any two webhooks signed by Shopify for the same app share the same key. An attacker who owns Shop A (a real, unprivileged merchant/dev store that has installed the target app) receives real, validly-HMAC'd webhooks for Shop A. They can then replay that exact `(raw_body, hmac-sha256 header)` pair to the app's webhook endpoint while substituting `x-shopify-shop-domain: shop-b.myshopify.com`. `HmacValidator.validate` recomputes HMAC over `raw_body` only, matches the header, and returns `true` — the forged request is treated as an authentic webhook for Shop B, even though the body/content actually originates from Shop A and the domain assertion was never covered by the signature.

### Impact Explanation
This breaks the tenant (shop) authentication boundary that host applications rely on the gem to enforce for inbound webhooks: `request.shop` is the only tenant-binding signal exposed by this gem's webhook API, and it is delivered to the app as already-"verified" data once `Registry.process` succeeds. Any app that (reasonably, per the gem's documented contract) trusts `WebhookMetadata#shop` after HMAC validation passes can be made to apply attacker-controlled webhook bodies against another merchant's tenant state (e.g. triggering shop-scoped side effects, cache/database writes, or redaction/data-request flows keyed by the spoofed shop). This is a cross-tenant access primitive within the scope of this gem's own verification logic, not a host-application misuse, since the gem provides no other mechanism to bind `shop` to the signature.

### Likelihood Explanation
Low-to-moderate: it requires the attacker to control at least one shop that has the target app installed (an unprivileged, self-service action — any developer can install a public/dev app on their own store) in order to obtain a validly-signed `(body, hmac)` pair, plus the ability to send arbitrary HTTP requests to the app's public webhook endpoint (which is Internet-reachable by design). No access token, `client_secret`, or session is needed — only observation of a webhook delivery to a shop the attacker controls.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`api-version`) header values in the signable payload used by `HmacValidator`, or otherwise document/enforce that `WebhookMetadata#shop` must be re-verified by the host app against the registered subscription owner before being trusted, rather than allowing the value to flow through as implicitly authenticated data. At minimum, `Registry.process` should not rely on body-only HMAC validation for a struct whose `shop` field is presented as authenticated metadata.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header `H` that Shopify computed with the app's shared `api_secret_key`.
2. Attacker replays this exact request to the app's webhook endpoint, keeping `B` and `H` unchanged but setting `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into `shop == "victim-shop.myshopify.com"` while `to_signable_string == B`: [7](#0-6) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and compares to `H` — this matches because the secret and body are unchanged, so validation succeeds: [8](#0-7) 
5. The app's `WebhookHandler#handle` receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)` as if it were an authentic webhook from the victim shop, even though neither Shopify nor the victim ever produced this event.

### Citations

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
