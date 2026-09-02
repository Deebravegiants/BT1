## Title
Webhook `shop`, `topic`, and `webhook_id` fields are not covered by the HMAC signature, enabling cross‑tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `ShopifyAPI::Webhooks::Registry.process` to dispatch and identify the tenant are read straight from unauthenticated HTTP headers. Anyone who can obtain one valid `(raw_body, hmac)` pair for the shared app secret can replay it with forged shop/topic headers and have it accepted as authentic for a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all parsed from headers that are never fed into the signable string: [2](#0-1) 

`HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` (i.e. the body) against the secret: [3](#0-2) 

`Registry.process` trusts the HMAC-validated request and then forwards the unauthenticated header-derived `shop`, `topic`, and `webhook_id` straight to the app's handler: [4](#0-3) 

This breaks the identity binding the app relies on: `shop_that_produced_the_HMAC == shop_the_handler_acts_on` does not hold. Only the raw body bytes are bound to the app's `api_secret_key`; the shop-domain, topic and webhook-id headers can be set to anything by whoever sends the HTTP request. Since the `api_secret_key` is shared across every shop that installs the app (it is not a per-tenant secret), any merchant who legitimately receives one valid webhook for their own shop can capture that `(body, hmac)` pair and resend it to the app's webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header rewritten to name a different shop. `Registry.process` will still validate successfully (the body/HMAC pair is valid) and will call the handler with `WebhookMetadata` claiming to be for the victim shop, topic, and webhook id chosen by the attacker.

This is exactly the "field acted on but not covered by the HMAC" identity-binding break: the equality that should hold — `shop authenticated by HMAC == shop the handler trusts and acts on` — is violated because `shop` (like `topic`/`webhook_id`) is taken from an unauthenticated header while the HMAC covers only the JSON body.

### Impact Explanation
Host applications built on this gem commonly key their per-shop data mutations directly off `WebhookMetadata#shop` (e.g., to update settings, delete resources, or process orders for "that" shop) since the gem presents the webhook as verified/authentic once `Registry.process` succeeds. An attacker who is any legitimate installer of the app (or who otherwise obtains one valid body/HMAC pair, e.g. via logs, browser network tab, or a compromised low-privilege environment) can trigger the app's webhook handler logic against an arbitrary victim shop identifier, or replay/relabel the same payload under a different topic/webhook id than the one Shopify actually sent. This is a cross-tenant confusion vector — data intended for shop A can be processed and stored as though it belongs to shop B — which matches the Critical "cross-tenant access" impact category, since the shop binding an app relies on for the webhook is not actually authenticated.

### Likelihood Explanation
Exploitation only requires the ability to POST an HTTP request to the app's public webhook endpoint with a previously-observed valid `(raw_body, hmac)` pair and forged headers — no access token, `api_secret_key`, or session is needed. The barrier is obtaining one legitimate webhook body/HMAC sample, which any shop that installs the app naturally receives from Shopify. This makes the attack straightforward for any current or former app installer, or anyone who can capture one webhook delivery in transit/logs.

### Recommendation
Include the routing/identity fields (`shop`, `topic`, `webhook_id`, `api_version`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signed body (e.g., verify them against Shopify's out-of-band API using the shop's own access token before trusting them), so that headers cannot be altered independently of the signed payload. At minimum, document that `Registry.process`'s `WebhookMetadata#shop`/`#topic`/`#webhook_id` are not authenticated by the HMAC and must not be used by host applications as a trust boundary for tenant identification without additional verification (e.g. cross-checking against the shop associated with the webhook subscription id via the Admin API).

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; Shopify delivers a genuine webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker records `(B, H)` (e.g., from their own server logs, since it was sent to them).
3. Attacker sends a new POST to the same webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid), but `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers; `Utils::HmacValidator.validate` succeeds because only `B` and `H` are checked: [5](#0-4) 
5. The handler executes with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, even though the payload/HMAC pair originated from `attacker-shop.myshopify.com`.

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
