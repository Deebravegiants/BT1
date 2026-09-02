This confirms the vulnerability. The webhook HMAC only signs the raw body, while `topic` and `shop` — the fields the app's handler actually acts on — come from unsigned headers.

### Title
Webhook `shop` and `topic` identity is trusted from unsigned headers while only the body is HMAC-verified, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook by computing an HMAC over the raw body only, using the app's shared `api_secret_key`, and then dispatches to the merchant's registered handler using the `shop`, `topic`, `webhook_id`, and `api_version` values taken directly from HTTP headers that are never included in that HMAC computation.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, not the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers: [1](#0-0) 

`Utils::HmacValidator.validate` verifies the HMAC solely against `to_signable_string`, i.e. the raw body, using the app-wide `Context.api_secret_key` (the same secret is used for every shop that installs the app, since Shopify apps share one client secret across all merchant installations): [2](#0-1) 

`Registry.process` then trusts `request.shop` and `request.topic` unconditionally after that body-only HMAC check passes, and passes them straight into the merchant-facing handler: [3](#0-2) 

The identity binding that should hold is: `HMAC(secret, signable_string)` should authenticate everything the handler acts on. Instead the equality that actually holds is `HMAC(secret, raw_body) == received_hmac`, while `shop`, `topic`, `webhook_id`, and `api_version` are read from headers entirely outside that signed string — i.e., **bytes verified (body) ≠ bytes/fields acted on (headers)**.

Because the secret is shared across all shops that installed the same app (not per-shop), an attacker who legitimately installs the target app on their own shop receives genuinely-signed webhook deliveries (e.g. `orders/create`) with a valid HMAC computed over a body they fully control. The attacker can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`) header with an arbitrary victim shop domain. `HmacValidator.validate` still succeeds because it only checks the untouched raw body, so `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: attacker_controlled_body, ...)`.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook authenticity: a request that Shopify never sent for the victim shop is delivered to the host application's handler tagged as coming from that victim shop, with attacker-chosen body content. Any host application that keys business logic, database writes, or downstream actions off `data.shop`/`data.topic` — the exact usage pattern shown in this gem's own webhook documentation and `WebhookMetadata` struct — can be manipulated into performing cross-tenant actions (e.g., injecting fake orders, uninstall notifications, GDPR redact requests, or other topic-specific side effects) attributed to a shop the attacker does not control. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only an unprivileged internet user who can install the target app on a shop they control (a normal, expected action for a public/embedded Shopify app) and can send arbitrary HTTP requests to the app's known webhook callback path. No access token, `api_secret_key`, or privileged account is needed — the attacker uses their own genuinely-issued webhook signature and simply forges the accompanying identity headers.

### Recommendation
Include the shop domain, topic, webhook id, and API version in the signed material verified by `HmacValidator` (e.g., bind them into `to_signable_string`, or independently authenticate them, such as cross-checking `shop` against the shop that owns the currently active session/subscription for that `webhook_id`), rather than trusting these header values purely because the body-only HMAC passed.

### Proof of Concept
1. Attacker creates their own Shopify development store and installs the target app, registering for `orders/create` webhooks (fully legitimate, unprivileged action).
2. Shopify delivers a webhook to the app's callback URL with headers `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`, and a body the attacker fully controls (attacker can craft the order that triggers this webhook).
3. Attacker intercepts/replays this exact request to the same app endpoint, but rewrites `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`, leaving the body and `X-Shopify-Hmac-Sha256` untouched.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `request.to_signable_string` (`@raw_body`), unaffected by the header change: [4](#0-3) 
5. The registered `WebhookHandler#handle` is invoked with `data.shop == "victim-shop.myshopify.com"` and attacker-controlled `data.body`, even though Shopify never sent this webhook for the victim shop.

### Citations

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
