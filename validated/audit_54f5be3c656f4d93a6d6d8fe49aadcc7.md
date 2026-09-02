### Title
Webhook `shop-domain` Header Is Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the identity of the merchant (`shop`) that a webhook belongs to from the `x-shopify-shop-domain` HTTP header, but the HMAC signature verified by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body. Any attacker who obtains one valid `(body, hmac)` pair — for example by installing the app on a shop they control and capturing a genuine webhook delivery — can replay that exact body/HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` will still report success because the header is not part of the signed content, and `Registry.process` will hand the forged shop identity straight to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from unauthenticated HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e., the body) and compares it to the `hmac` header: [3](#0-2) 

`Webhooks::Registry.process` trusts this validation and then forwards the header-derived `request.shop` directly to the consuming application's handler as the authoritative tenant identifier: [4](#0-3) 

This breaks the identity binding the report describes as "a field acted on but not covered by the HMAC": the `shop` value that the handler acts on (`WebhookMetadata#shop`) is not the same as the `shop` value cryptographically authenticated by the HMAC (which authenticates nothing about the sender's identity at all, only the body bytes). Since the webhook HTTP endpoint is a public, unauthenticated internet-facing endpoint (that is the entire point of webhooks), any unprivileged internet user who can obtain one valid `(body, hmac)` pair — trivially, by installing the app themselves on a store they control and capturing the delivered request — can resubmit that same body/hmac with a forged `shop-domain` header pointing at a victim merchant. The gem will validate it as authentic and pass the forged shop identity to the host application.

### Impact Explanation
This allows cross-tenant confusion/spoofing: a host application that keys its business logic (e.g., "update order X for shop Y", "look up the session/access token for shop Y") off `WebhookMetadata#shop` — which is exactly the contract this gem hands to consumers — can be tricked into applying an attacker-controlled webhook body under a victim shop's identity. Depending on the webhook topic (e.g., `app/uninstalled`, `customers/data_request`, `orders/create` style topics), this can result in cross-tenant data corruption or processing of attacker data attributed to another merchant, matching the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Moderate-to-high: the attacker only needs to be able to install the target app on a shop they control (or otherwise obtain one legitimate webhook delivery, which many app models allow to any developer/merchant), capture the raw body and its valid HMAC, then POST it directly to the app's public webhook URL with a different `shop-domain` header. No access token, `api_secret_key`, or privileged credential is required — the vulnerability lives entirely in this gem's failure to bind the header-derived identity to the signed content.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) values in the signed/verified content, or otherwise cryptographically bind the `x-shopify-shop-domain` header to the HMAC before trusting it as the tenant identifier passed to `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated header data and must not be trusted to select a merchant's access token/session without additional out-of-band verification (e.g., cross-checking against an existing stored session for that shop before acting).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they control) and lets Shopify deliver one webhook, e.g. `orders/create`, capturing the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent.
2. Attacker crafts a new HTTP POST to the app's webhook endpoint using:
   - the identical raw body and `x-shopify-hmac-sha256` value captured above,
   - `x-shopify-topic: orders/create`,
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (forged).
3. `ShopifyAPI::Webhooks::Request.new` parses this into a request object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (the raw body only) and matches successfully because the body/hmac pair is genuinely valid — the forged `shop-domain` header was never part of the signed content.
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the host application to process attacker-supplied data as if it originated from `victim-shop.myshopify.com`.

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
