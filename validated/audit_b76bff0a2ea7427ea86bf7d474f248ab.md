### Title
Webhook `shop-domain` identity is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body against the app's shared `client_secret`. The `shop-domain` header — which the gem extracts and hands to the host application as the tenant identity for the event — is never included in the signed material, so its value is not bound to the signature that "proves" the webhook is genuine.

### Finding Description
`Utils::HmacValidator.validate` computes/verifies the signature over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw body — no headers are part of the signed payload: [2](#0-1) 

`shop` is read straight from the (unsigned) `shopify-shop-domain` / `x-shopify-shop-domain` header: [3](#0-2) 

`Registry.process` then validates only the body HMAC and immediately trusts `request.shop` as the tenant identity forwarded to the app's handler: [4](#0-3) 

The identity binding that should hold is:
`shop_header == shop_that_the_app_secret_owner_actually_signed_for`

What is actually checked is only:
`HMAC_sha256(client_secret, raw_body) == received_hmac`

Because the app's `client_secret` (`Context.api_secret_key`) is a single, app-wide secret shared across every merchant who installs the app — not a per-shop secret — any merchant who has installed the app can trigger a legitimate webhook to their own store and thereby obtain a valid `(raw_body, hmac)` pair signed with that same shared secret. That pair remains valid for *any* value of the `shop-domain` header, since the header is excluded from `to_signable_string`. The attacker can then POST that captured body/HMAC pair directly to the app's public webhook endpoint while substituting a victim shop's domain in the `x-shopify-shop-domain` header. `Registry.process` will accept it as authentic and hand `WebhookMetadata.new(... shop: request.shop ...)` — carrying the forged victim shop — to the app's handler.

### Impact Explanation
This is a cross-tenant identity-binding break: a low-privilege user (any merchant who has installed the app, not a privileged operator) can make the app process attacker-controlled webhook data under another tenant's identity. If the host application uses `WebhookMetadata#shop` to select which merchant's records to create/update/delete (a normal and expected usage pattern this gem's docs promote), the attacker can inject or corrupt data attributed to a shop they do not own — a cross-tenant access impact.

### Likelihood Explanation
Requires only that the attacker be an app installer (an "unprivileged internet user" relative to other tenants) able to trigger at least one real webhook delivery for their own shop, and that they can send an arbitrary HTTP POST to the app's public webhook endpoint (a standard, internet-reachable URL by design). No access to the app's `client_secret`, TLS interception, or victim credentials is required — only reuse of a signature the gem itself never binds to the shop identity it exposes.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the signed material verified for webhooks, or — since Shopify's webhook HMAC scheme only ever signs the body — have `Registry.process` cross-check `request.shop` against the shop that the specific webhook subscription was registered for (tracked by the app) before invoking the handler, rather than trusting the header value implicitly. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated relative to the HMAC check and must not be used as a sole tenant key by the host app.

### Proof of Concept
1. Attacker installs the target app on their own (attacker-owned) Shopify store, obtaining the app's shared `client_secret` implicitly usable only via legitimate delivery — they do not need the secret itself.
2. Attacker triggers a real event on their own store (e.g., updates a product) causing Shopify to deliver a webhook to the app's endpoint with a valid `raw_body` and `x-shopify-hmac-sha256` computed with the app's shared secret.
3. Attacker captures this `(raw_body, hmac)` pair (e.g., by proxying their own store's webhook, or via a local test endpoint they control that also receives the same class of message).
4. Attacker replays this exact `raw_body` + `hmac` header to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, raw_body)`: [5](#0-4) 
6. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, and — if the host app uses `shop` to route data mutations, as the gem's own usage docs suggest — processes attacker data under the victim's tenant.

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
