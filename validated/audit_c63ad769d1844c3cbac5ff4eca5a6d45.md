### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop` (and `topic`, `api_version`, `webhook_id`) values that are subsequently used to attribute the webhook to a specific merchant are taken from HTTP headers that are **not** included in the signed content. This breaks the intended identity binding of `shop-domain header == shop authenticated by HMAC`.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines the signable content as only the raw body: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` fields are all pulled straight from HTTP headers, none of which are part of `to_signable_string`: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` (the raw body) and compares it with the `hmac` field: [3](#0-2) 

`Webhooks::Registry.process` uses this single HMAC check as the sole authentication gate, then dispatches the handler using the *unverified* `request.shop` header value: [4](#0-3) 

Because the app's `api_secret_key`/`old_api_secret_key` is a single, app-wide secret (not shop-specific), any body that was legitimately signed by Shopify for *any* installed shop (including a shop the attacker legitimately controls/installed the app on) produces a valid HMAC regardless of which `x-shopify-shop-domain` header accompanies it. The equality the code implicitly assumes — `shop value trusted by HMAC == shop value used to route/process the webhook` — does not hold: the HMAC only binds the body bytes, while the shop identity used downstream is taken from an out-of-band, unauthenticated header.

An unprivileged actor who can install the app on their own store (a legitimate, unprivileged action) will receive genuinely-signed webhooks (valid `hmac-sha256` over the body) from Shopify for their own shop. They can then replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) header value naming a different, victim shop. `HmacValidator.validate` will still return `true` because it never inspects the shop header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop.

### Impact Explanation
This is a cross-tenant confusion primitive: the app's webhook consumer will process attacker-controlled data (order/customer/GDPR payloads, etc., replayed from the attacker's own shop or crafted within the range of fields the attacker's own store lets them control) under the identity of an arbitrary victim shop domain, because `shop` is trusted without being bound to the signed bytes. Depending on how the host app persists/acts on webhook data keyed by `data.shop` (e.g., updating order records, customer PII, or GDPR compliance state for "that shop"), this can lead to cross-tenant data corruption or injection — meeting the "cross-tenant access" bar.

### Likelihood Explanation
Any developer/merchant can install the target app on their own shop (no privileged access required), which is enough to obtain genuinely HMAC-signed webhook bodies for arbitrary permitted topics. Replaying that request to the app's public webhook URL with a modified `shop-domain` header requires only a basic HTTP client — no access to the app's `client_secret`, tokens, or TLS interception is needed.

### Recommendation
Bind the shop identity into the HMAC verification surface, e.g., verify the `x-shopify-shop-domain` (and ideally `topic`/`webhook-id`) headers against a value cryptographically tied to the signed payload, or require host applications to cross-check the shop header against an independently known/authorized shop for the given webhook topic/resource before trusting `WebhookMetadata#shop`. At minimum, `VerifiableQuery#to_signable_string` for webhook requests should incorporate the shop domain header so a mismatch invalidates the HMAC.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled shop `attacker.myshopify.com`.
2. Trigger a webhook topic the app subscribes to (e.g., `orders/create`); Shopify sends a POST with a valid `x-shopify-hmac-sha256` computed over the raw JSON body using the app's `api_secret_key`.
3. Capture `raw_body` and `x-shopify-hmac-sha256`.
4. Resend the identical `raw_body`/`x-shopify-hmac-sha256` to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
5. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) returns `true` because it only checks the body signature; `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) invokes the handler with `shop: "victim.myshopify.com"`, causing the app to process attacker data under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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
