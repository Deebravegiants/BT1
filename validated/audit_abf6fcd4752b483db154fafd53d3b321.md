### Title
Webhook `shop`/`topic` fields trusted from unauthenticated headers while only the body is HMAC-verified, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate`, but the `shop`, `topic`, and `webhook_id` values that the handler receives and acts on are read directly from HTTP headers that are never included in the signed content. This breaks the identity binding `HMAC-covered bytes == data the app trusts as originating from a given shop`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are read straight from headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates only the body HMAC, then immediately forwards the unauthenticated header-derived `shop`/`topic`/`webhook_id` to the app's handler as trusted metadata: [3](#0-2) 

`Utils::HmacValidator.validate` and `validate_signature` confirm the signature check is body-only, comparing `verifiable_query.to_signable_string` (the raw body) against the computed HMAC — nothing about the shop header is part of the signed input: [4](#0-3) 

Because the webhook HMAC is computed with the app's single, shared `api_secret_key` (identical for every shop that installs the app), any actor who has installed the app on any shop can capture a legitimately-signed `(body, hmac)` pair from a real webhook delivery to their own shop, then replay that exact body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header for a different, victim shop. `HmacValidator.validate` will still pass (it only checks the body), and `Registry.process` will hand the handler a `WebhookMetadata` object whose `shop` field claims to be the victim shop even though the payload was never generated for, or by, that shop.

### Impact Explanation
This breaks the equality that should hold: `shop value trusted by the handler == shop value bound by the HMAC signature`. Downstream app logic that keys multi-tenant behavior off `WebhookMetadata#shop` (e.g., updating per-shop records, processing `app/uninstalled`, `shop/redact`, `customers/data_request`, or writing order/customer data attributed to a shop) can be tricked into acting on forged data attributed to a shop the attacker does not control — a cross-tenant confusion/injection primitive reachable by any party who can install the app on a shop they control (a low, effectively unprivileged bar) and observe one real webhook delivery.

### Likelihood Explanation
Moderate-to-high: exploitation requires only (1) installing the target app on an attacker-controlled shop to legitimately receive one signed webhook, and (2) sending an HTTP request to the app's public webhook endpoint with a forged `shop-domain`/`topic` header while reusing the captured body and HMAC. No access to the app's `client_secret`, an access token, or the victim shop's credentials is needed — only observation of the shared-secret-signed body, which any installing party can obtain.

### Recommendation
Include the authenticating identity fields (at minimum `shop`, and ideally `topic`/`webhook_id`) in the HMAC-signed content that `to_signable_string` returns, or otherwise cryptographically bind them (e.g., derive/verify `shop` from a value included in the signed payload rather than trusting the header verbatim). Until then, document prominently that `Registry.process`'s `WebhookMetadata#shop`/`#topic` are not authenticated by the HMAC check and that host applications must independently verify the shop against their own session store before acting on webhook content.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) to receive a legitimately Shopify-signed request: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the shared `api_secret_key`), `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Replay a request to the app's webhook endpoint with the same body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com` (and/or a different `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `OpenSSL.secure_compare(compute_signature(request.to_signable_string, secret), H)` — this still passes because `to_signable_string` is just `B`. [3](#0-2) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"`, `topic` and `body` from the attacker-controlled payload, and processes it as authentic data for the victim shop.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
