## Title
Webhook `shop` (and `topic`/`webhook_id`) headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from only the raw HTTP body, while the `shop-domain`, `topic`, and `webhook-id` headers are read separately and never included in the HMAC input. `Registry.process` validates the HMAC and then trusts `request.shop` as the tenant identity forwarded to the app's webhook handler. Because the shop identity is not cryptographically bound to the signed payload, a valid `(body, hmac)` pair obtained from one merchant's webhook can be replayed with a different `shop-domain` header and will still pass `HmacValidator.validate`.

### Finding Description
`Utils::HmacValidator.validate` computes the signature exclusively over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` is defined to return only `@raw_body`: [2](#0-1) 

Meanwhile `shop`, `topic`, and `webhook_id` are parsed straight from HTTP headers with no cryptographic tie to the signed body: [3](#0-2) 

`Registry.process` validates the HMAC and then unconditionally forwards `request.shop` into `WebhookMetadata`, which is the tenant-identifying field the host application's handler uses to route/store data per shop: [4](#0-3) [5](#0-4) 

The identity binding broken here is: `HMAC-signed bytes == raw_body` but `data.shop (trusted tenant identity) == request.shop (unauthenticated header)`. The `shop` header is never part of the signable string, so the HMAC check provides no guarantee about which shop a given signed body belongs to.

### Impact Explanation
Any unprivileged party who can obtain one genuinely-signed `(body, hmac)` pair for the app's webhook endpoint — trivial for an attacker who installs the app on their own shop and receives one legitimate webhook, since the request is delivered over plain HTTP(S) to a public callback URL — can replay that exact body/HMAC combination while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a different, victim shop's domain. `HmacValidator.validate` still returns `true` because only the body bytes are checked, and `Registry.process` will hand the handler a `WebhookMetadata` whose `shop` is the attacker-chosen value. If the host app uses `data.shop` to key per-tenant storage, trigger per-tenant side effects, or make decisions about which merchant's data is being updated (as the gem's own documentation instructs, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), this results in cross-tenant data confusion/corruption attributed to an arbitrary victim shop — a cross-tenant access issue.

### Likelihood Explanation
Exploitation requires no secrets, no TLS interception, and no privileged access — only the ability to send an HTTP POST to the app's public webhook endpoint with a previously-observed valid body+HMAC pair and an attacker-chosen shop header, which is achievable by any actor who has installed the app (even on a throwaway/trial shop) and captured one real webhook delivery.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header values in the signable string used for HMAC computation, or otherwise cryptographically bind the shop identity to the signed body (e.g., verify that `request.shop` matches a shop known to have an active, correctly-registered webhook subscription before dispatching to the handler) instead of trusting the header value that is disjoint from what the HMAC actually covers.

### Proof of Concept
1. App receives a legitimate webhook for `attacker-shop.myshopify.com` with body `{"id":1}` and a correct `x-shopify-hmac-sha256` header computed over that body.
2. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate` recomputes HMAC only over `@raw_body`, which matches — validation passes: [6](#0-5) 
4. `Registry.process` calls the handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: {"id"=>1}, ...)`, so the app processes attacker-supplied data as if it belongs to `victim-shop.myshopify.com`. [7](#0-6)

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
