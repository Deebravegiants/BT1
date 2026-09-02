## Title
Webhook `shop` (and `topic`/`webhook-id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing via replay of a self-owned webhook - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. However, the `shop` field — which is passed downstream to the app's webhook handler as the authoritative tenant identifier — is taken from an HTTP header that is *not* included in the HMAC-signed material. Any user who can obtain one genuinely-signed webhook for a shop they control (trivial: install the app on their own store and trigger any webhook) can replay that exact body+HMAC to the app's webhook endpoint while swapping only the `X-Shopify-Shop-Domain` header to a victim shop, causing the library to accept it as authentic and hand the handler a `WebhookMetadata` object attributed to the victim shop.

### Finding Description
The webhook request wraps the incoming HTTP request and implements `Utils::VerifiableQuery`: [1](#0-0) 

`hmac` is derived from the `hmac-sha256` header, and `to_signable_string` returns **only `@raw_body`**. Crucially, `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, but none of them are folded into `to_signable_string`.

`Registry.process` validates authenticity using exactly this signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, verifiable_query.to_signable_string)` and compares it to the received HMAC: [3](#0-2) 

Because `to_signable_string` is body-only, the HMAC check establishes only "this body byte-sequence was HMAC'd with the app's secret at some point" — it proves nothing about which shop, topic, or webhook-id the signature was actually issued for. Yet `request.shop` (the unauthenticated header) is trusted as the tenant key and forwarded straight into the handler:

```ruby
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

This is the direct structural analog of the reported bug class: a signature (the H-01 report's replayable signature; here, the webhook HMAC) validates a payload, but a separate identity-binding field acted upon by the receiver (owner index in H-01; `shop` here) is not itself covered by that signature. The binding that should hold is:

`shop authenticated by HMAC == shop used as the tenant/session key by the handler`

but the code only guarantees:

`body authenticated by HMAC == raw_body`,

leaving `shop` completely attacker-controlled at the HTTP layer.

### Impact Explanation
Any user capable of installing the app on a shop they control (which is the normal, unprivileged install flow for any Shopify app) receives genuinely HMAC-signed webhooks for their own shop. Because the shop header is outside the signed material, that same valid `(body, hmac)` pair can be replayed to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to any victim shop domain. `HmacValidator.validate` still succeeds (it only checks the body), so `Registry.process` invokes the app's handler with `WebhookMetadata#shop` set to the victim's domain. Any host application that uses `shop` from webhook metadata to select a session/store, write data, revoke access, or otherwise perform tenant-scoped actions will perform those actions against the wrong tenant, using data supplied by the attacker's own account — i.e., cross-tenant access/data confusion, achieved by an unauthenticated (with respect to the victim) internet user.

### Likelihood Explanation
High. No secrets, tokens, or elevated privileges are required — only a free/normal app installation on any shop (including the attacker's own), which yields a legitimate signed webhook that can be replayed indefinitely with an altered shop header via a plain HTTP request to the app's public webhook endpoint.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material used for verification, or otherwise cryptographically bind them to the signature (e.g., verify against a value obtained independently, such as looking up the webhook's own subscription record by `webhook_id` and cross-checking the expected shop, rather than trusting the header verbatim). At minimum, `Webhooks::Request#to_signable_string` should not diverge from the actual identity fields that `Registry.process`/`WebhookMetadata` treat as authoritative.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any webhook subscribed by the app (e.g. `orders/create`), capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Attacker resends that exact body and HMAC header to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally alters `X-Shopify-Topic`/`X-Shopify-Webhook-Id`, also unauthenticated).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `raw_body` [4](#0-3) .
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)` and performs shop-scoped processing believing it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
