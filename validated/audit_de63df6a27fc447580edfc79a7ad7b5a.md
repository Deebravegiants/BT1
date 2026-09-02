This confirms the finding: the gem's own documentation (`docs/usage/webhooks.md` line 125) explicitly states that `Registry.process` "will verify the request did indeed come from Shopify" via the HMAC check, then trusts `data.shop` — which is exactly the field NOT covered by that HMAC.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the raw request body against the HMAC-SHA256 signature, while the `shop` value passed to the app's handler is read from an unsigned HTTP header. This breaks the intended binding "shop authenticated by HMAC == shop trusted by the handler for tenant identification," letting an attacker who controls one legitimately-signed webhook payload relabel it as belonging to a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac` is derived from the `hmac-sha256` header: [1](#0-0) 

`shop`, however, is read straight from the `shop-domain` header, which participates in `to_signable_string` nowhere: [2](#0-1) [3](#0-2) 

`HmacValidator.validate` verifies exactly the string returned by `to_signable_string` against the secret — i.e., only the body: [4](#0-3) 

`Registry.process` accepts the request once that body-only HMAC check passes, then forwards the unauthenticated `request.shop` straight to the app's handler as the tenant identifier: [5](#0-4) 

The equality the gem implicitly promises but does not enforce is: `shop bound by HMAC == shop delivered to WebhookMetadata`. In reality the HMAC binds only the body bytes; the `shop` field is parsed but never verified. The gem's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify" and then hands `data.shop` to the handler as the shop domain of the webhook, reinforcing that callers are meant to trust this value once `process` succeeds: [6](#0-5) [7](#0-6) 

Because the app's `client_secret` (and therefore the HMAC key) is shared across every shop the app serves, any attacker who is a merchant with the app installed on their own store (an unprivileged internet user relative to other tenants) can capture one webhook Shopify sends them — the body/HMAC pair is valid for their own shop's event — and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop. `HmacValidator.validate` still succeeds because the raw body was not modified, but `request.shop` (and thus `WebhookMetadata#shop` passed to the app's handler) now falsely claims the victim's tenant.

### Impact Explanation
This is a cross-tenant identity-confusion vector delivered entirely through this gem's own webhook-processing API: an app that keys any per-shop side effect (queued jobs, database writes, cache invalidation, session lookups) off `WebhookMetadata#shop` after `Registry.process` returns success will attribute attacker-controlled event data to an arbitrary victim shop domain, without ever needing the victim's access token or `client_secret`. This matches the "cross-tenant access" class of impact — data belonging to shop A's webhook body is delivered as if it were shop B's, purely because the tenant-identifying field is outside the cryptographic binding the gem performs.

### Likelihood Explanation
Likelihood is Medium: an attacker needs only the credentials any real merchant already has — the ability to install the app on their own store and trigger/capture one webhook event (e.g., create an order or update a product) — plus the ability to POST an HTTP request with a spoofed `X-Shopify-Shop-Domain`/`shopify-shop-domain` header. No access token, `client_secret`, or privileged role is required, and the vulnerable code path (`Registry.process` → `HmacValidator.validate` → handler dispatch) is exercised on every webhook delivery in normal integration usage.

### Recommendation
Extend `Utils::VerifiableQuery#to_signable_string`/`HmacValidator` usage for webhooks so that the `shop` (and ideally `topic`, `webhook_id`) header values are cryptographically bound, e.g., by including them in the signed payload comparison, or by requiring `Registry.process` callers to additionally confirm `request.shop` against an independently-authenticated session/shop record before trusting it — analogous to fixing `setMaxStakeAmount()` by only special-casing the "unlimited" branch instead of unconditionally trusting an unchecked input. At minimum, the gem should document prominently that `data.shop` in `WebhookMetadata` is *not* authenticated by the HMAC check and must be cross-validated by the host app against its own shop/session store before being used as a tenant key.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers an event (e.g., updates a product) so Shopify sends a webhook to the app's endpoint.
2. Attacker captures the raw POST: headers include `x-shopify-hmac-sha256: <valid HMAC over body>` and `x-shopify-shop-domain: attacker.myshopify.com`; body is the JSON payload.
3. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses `shop` from the (attacker-controlled) header: [2](#0-1) 
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `raw_body` and succeeds because the body was untouched: [8](#0-7) 
6. The handler is invoked with `WebhookMetadata.new(..., shop: request.shop, ...)`, so `data.shop == "victim.myshopify.com"` even though the event data belongs to `attacker.myshopify.com`: [9](#0-8) 
7. Any host-app logic that uses `data.shop` to route the payload to per-tenant storage now attributes attacker-controlled webhook content to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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

**File:** docs/usage/webhooks.md (L10-16)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L125-135)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
