### Title
Webhook `shop-domain` (and `topic`/`api_version`/`webhook_id`) headers are not covered by the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw request body only, but the `shop-domain`, `topic`, `api_version`, and `webhook_id` values used by `ShopifyAPI::Webhooks::Registry.process` to dispatch and identify the webhook are taken from unauthenticated HTTP headers that are never included in the signed content.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC strictly from `to_signable_string` and compares it against the `hmac` accessor: [2](#0-1) 

Meanwhile, `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all pulled directly from HTTP headers with no cryptographic binding to the body or to each other: [3](#0-2) 

`Registry.process` verifies only `Utils::HmacValidator.validate(request)` and then dispatches the handler using the unauthenticated `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version`: [4](#0-3) 

Because none of these header-derived fields are part of the signed payload, the equality that should hold — **shop the HMAC was generated for == shop the handler processes data for** — is not enforced. Anyone who possesses one genuine `(raw_body, hmac)` pair (e.g., the attacker's own tenant installation of the app, which legitimately receives real, correctly-signed webhook deliveries from Shopify for their own shop) can replay that exact `raw_body` + `hmac-sha256` value to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header. `HmacValidator.validate` will still pass because it only checks the body bytes, and the handler will then process the request attributing it to the attacker-chosen shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: `shop verified by HMAC` (none, since `shop` isn't signed) vs. `shop the webhook handler acts on` (attacker-controlled header). An attacker who is a legitimate but unprivileged merchant/tenant of a multi-tenant app built on this gem can forge webhook deliveries that are processed as if they belong to a victim shop, since the app's webhook endpoint is public and unauthenticated by design (that's how Shopify webhooks work), and the only verification performed (`HmacValidator.validate`) never binds the shop identity to the signature. Depending on what the app's `WebhookHandler#handle` implementations do with `data.shop` (e.g., look up/select which tenant's records to modify, mark shop-level state such as uninstall/redact, etc.), this can result in cross-tenant data corruption or state confusion — this classifies as Critical: cross-tenant access.

### Likelihood Explanation
Exploitation requires the attacker to have access to at least one genuine `(raw_body, hmac)` pair, which they can obtain without needing the app's `client_secret`/`api_secret_key` simply by being a legitimate installer of the app on their own shop and capturing a webhook Shopify sends them (e.g. via their own endpoint logs), since this does not require compromising TLS or exfiltrating secrets belonging to a victim. The replay itself only requires sending a normal HTTP POST to the app's public webhook route, no elevated privileges needed.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook_id`) header values in the string that is HMAC-verified, or otherwise cryptographically bind them to the raw body before comparing signatures, so that a valid signature can only be replayed for the exact shop/topic it was generated for. Alternatively/additionally, document and encourage handler implementations to independently verify that `data.shop` corresponds to a shop with an active, matching session/installation before acting on the payload.

### Proof of Concept
1. App is a multi-tenant Shopify app using this gem; attacker installs the app on their own shop `attacker.myshopify.com` and configures a webhook handler for `topic`.
2. Shopify delivers a legitimate webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's `api_secret_key`), plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures `(B, H)` from their own endpoint logs/traffic.
4. Attacker POSTs the same body `B` and header `X-Shopify-Hmac-Sha256: H` to the app's webhook endpoint again, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B`/`H` (`lib/shopify_api/utils/hmac_validator.rb` L26-31), then dispatches the handler with `shop: "victim.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb` L198-199), causing the app to process attacker-supplied data as if it originated from the victim's shop.

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
