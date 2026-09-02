## Title
Webhook `shop`/`topic`/`webhook_id` identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while `ShopifyAPI::Webhooks::Registry.process` trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken straight from unauthenticated HTTP headers when dispatching to the registered handler. Any party who can obtain one valid `(body, hmac)` pair — e.g., by legitimately installing the app on their own store — can replay that pair to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header, and the signature will still validate, since those identity fields sit outside the signed data.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` (used by `Registry.process`) verifies the HMAC using exactly that `to_signable_string` value, so it only proves the body bytes were signed with `Context.api_secret_key` — it says nothing about which shop, topic, or webhook the payload belongs to: [3](#0-2) 

`Registry.process` then forwards these unauthenticated fields straight into the handler's `WebhookMetadata`: [4](#0-3) 

This is analogous to the referenced Optimism Portal bug: a security check (the HMAC/gas check) is performed against a narrower scope than what is actually acted upon (only the SSTORE buffer / only the body bytes), while other state that downstream logic relies on (the forwarded call's gas / the `shop` identity used by the handler) is left unguarded. Here the binding that breaks is:
`shop authenticated by HMAC` ≠ `shop stored/used as the identity key by the handler`.

Because a single `api_secret_key` is shared across every shop that installs the app, any unprivileged user who installs the app on their own store can:
1. Receive a legitimate webhook `(body, x-shopify-hmac-sha256, x-shopify-shop-domain: attacker.myshopify.com)` from Shopify for a genuine event they control (e.g., `orders/create` on their own store, with attacker-chosen order content).
2. Replay that exact `body` + `hmac` header to the app's public webhook endpoint, but swap `x-shopify-shop-domain` to `victim.myshopify.com` (and/or swap `x-shopify-topic`/`x-shopify-webhook-id`).
3. `HmacValidator.validate` still passes because the signature only covers the unchanged body.
4. `Registry.process` dispatches to the handler with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker-controlled content>, topic: ...)`.

### Impact Explanation
If the host application's webhook handler uses `WebhookMetadata#shop` as the session/tenant key (the documented and expected usage pattern — the gem returns `shop` from `request.shop` specifically so handlers can act on behalf of that shop), the attacker can inject arbitrary, attacker-controlled payload content that gets processed as if it originated from the victim's shop. Depending on the handler, this crosses the tenant boundary (data written to, or actions performed against, a victim shop's store using the victim's stored access token while the actual content is attacker-controlled) — this maps to the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any unprivileged user can install the target app on a free/dev store, capture one valid webhook body+HMAC pair for an event whose content they control, and replay it with a forged `shop-domain` header. No access token, `api_secret_key`, or privileged access is required — only the ability to receive one legitimate webhook and to send an HTTP request to the app's public webhook endpoint.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` values in the signed data (or otherwise independently verify that the `shop-domain` header corresponds to a shop with an active installation/session before trusting it), so that `HmacValidator.validate` binds the signature to the specific shop and topic the payload claims to represent, not just the raw body bytes.

### Proof of Concept
```ruby
# Attacker installs the app on their own store and captures a legitimate webhook:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_valid_hmac, # valid because body was really signed by api_secret_key
  "x-shopify-shop-domain" => "attacker.myshopify.com",
}
body = attacker_controlled_order_json # attacker crafted the order content on their own store

# Attacker replays it against the app's public webhook endpoint, forging the shop:
forged_headers = headers.merge("x-shopify-shop-domain" => "victim.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate succeeds (body unchanged); handler.handle receives
#    WebhookMetadata(shop: "victim.myshopify.com", body: attacker_controlled_order_json, ...)
```

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
