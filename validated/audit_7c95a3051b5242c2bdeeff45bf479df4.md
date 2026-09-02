The gem's webhook signature scheme is the concrete analog to the reported "identity binding bypass" pattern: an attacker-controllable field (`shop`) is *acted upon* by the library but is **not covered by the HMAC**, exactly matching the report's bug class. [1](#0-0) [2](#0-1) 

### Title
Webhook `shop`/`topic` fields are trusted but excluded from HMAC verification, enabling cross-tenant webhook spoofing - (`File: lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers and never included in the HMAC-signed content. `Registry.process` validates the HMAC against the body alone and then hands the header-derived `shop`/`topic` straight to the app's handler as trusted tenant-identifying data, breaking the intended binding between "bytes verified" and "bytes acted on."

### Finding Description
`Utils::HmacValidator.validate(request)` computes the HMAC over `request.to_signable_string`, which is defined as `@raw_body` only: [3](#0-2) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are parsed from separate HTTP headers (`shopify-shop-domain`/`x-shopify-shop-domain`, `shopify-topic`, etc.) that are not part of the signed payload: [4](#0-3) 

`Registry.process` validates only the body's HMAC, then constructs `WebhookMetadata` using the unauthenticated header values and dispatches it to the registered handler as the "verified" webhook shop/topic: [2](#0-1) 

The equality that should hold is: `hmac_computed_over(shop, topic, webhook_id, api_version, body) == hmac_received`. Instead, only `hmac_computed_over(body) == hmac_received` is checked, while `shop`/`topic` are consumed downstream as if they were also verified. This is the same class of bug as the locked-voter report: a value that is *acted upon* (the governor/locker binding there; the `shop` tenant identity here) is not actually checked against the value covered by the trusted proof (governor equality there; HMAC coverage here).

### Impact Explanation
Because the HMAC secret (`Context.api_secret_key`) is identical for every shop that installs the same app, any unprivileged internet user who can obtain one genuine `(body, hmac)` pair for the app — trivially done by installing the app on a free Shopify **development store** they control and capturing a real webhook delivery — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` still passes (it never inspected the header), and the handler receives `WebhookMetadata` with `shop` pointing at the victim tenant. Any app logic that uses `data.shop` to scope per-tenant state (which is the gem's documented usage pattern) will act on/write data under the victim's identity, i.e. cross-tenant access/injection using only the attacker's own legitimately-issued webhook traffic.

### Likelihood Explanation
High. No access token, `client_secret`, or privileged account is required — only the ability to install the app on any shop (including a self-owned free dev store) to harvest one valid signed body, and the ability to send an arbitrary HTTP POST to the app's public webhook endpoint. The attack requires no cryptographic break, only header substitution.

### Recommendation
Include the identity-binding fields (`shop`, `topic`, and ideally `webhook_id`) in the HMAC-signed content, or otherwise cryptographically bind them (e.g., by having `to_signable_string` incorporate the header values), so that `Utils::HmacValidator.validate` cannot succeed unless the shop/topic match what Shopify actually signed for that specific delivery.

### Proof of Concept
1. Install the target app on an attacker-controlled Shopify development store `attacker-shop.myshopify.com` and trigger any webhook subscription (e.g. `app/uninstalled`), capturing the raw POST body and the `x-shopify-hmac-sha256` header — this HMAC is valid because `Utils::HmacValidator.validate` only signs `@raw_body`.
2. Replay this exact `(body, x-shopify-hmac-sha256)` pair to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com` and/or `x-shopify-topic` with a different registered topic.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which passes because it never checked the header values against the signature.
4. The handler is invoked with `WebhookMetadata.new(topic: "attacker-chosen-topic", shop: "victim-shop.myshopify.com", body: ..., ...)`, and any app logic keyed on `data.shop`/`data.topic` now operates under the victim's tenant identity despite the request never having been signed for that shop or topic.

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
