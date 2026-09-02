This confirms the documented gem usage: the docs explicitly state that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0) , and that `data.shop`/`data.topic` are trustworthy fields handed to the app's handler [2](#0-1) . That guarantee is false: the HMAC only covers the raw body, not the shop/topic/webhook-id headers.

### Title
Webhook shop/topic identity spoofing via HMAC that only covers the raw body, not the trust-bearing headers - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` purely from HTTP headers, while `to_signable_string` (the value protected by HMAC) is only the raw request body [3](#0-2) . `Registry.process` validates the HMAC and then unconditionally trusts `request.shop` and `request.topic` to route to a handler and populate `WebhookMetadata` [4](#0-3) . Because the identity fields (shop, topic, webhook_id) are never part of the signed material, they can be freely substituted by anyone able to POST to the app's public webhook endpoint, as long as they can supply *any* previously-valid `(raw_body, hmac)` pair signed with the app's shared `api_secret_key`.

### Finding Description
The binding that should hold is:
`hmac == HMAC(api_secret_key, raw_body || shop || topic)`, i.e., the identity of the shop/topic the app acts on should be bound to the same signature that authenticates the request.

Instead, the gem computes:
- `HmacValidator.validate` calls `verifiable_query.to_signable_string`, which for `Webhooks::Request` returns only `@raw_body` [5](#0-4) [6](#0-5) .
- `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from attacker-controllable HTTP headers with no cryptographic binding to the signed body [7](#0-6) .
- `Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., only that *some* valid body+hmac pair was presented) before trusting `request.topic` to select a handler and `request.shop` to construct `WebhookMetadata` passed to the app's handler [4](#0-3) .

The `api_secret_key` used for HMAC is the app-wide client secret — the same secret is used to sign every shop's webhooks for the app, not a per-shop secret [8](#0-7) . Consequently, an unprivileged attacker who has installed the app on their own shop (or who has captured any single legitimate webhook delivery for any shop, e.g. from browser dev tools, logs, or a proxy) obtains a `(raw_body, hmac)` pair that is valid for the shared secret regardless of which shop it was originally destined for. They can then POST that exact `raw_body` and `hmac` to the app's public webhook endpoint while freely rewriting the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, and `X-Shopify-Webhook-Id` headers to name a different (victim) shop or a different topic. `HmacValidator.validate` will still pass because it only checks the body against the secret, so `Registry.process` will dispatch the (attacker-chosen) body to the (attacker-chosen) topic handler while reporting it as coming from the (attacker-chosen) shop.

This directly matches the "field acted on but not covered by HMAC" identity-binding failure class: the shop/topic identity that downstream application code trusts and acts on (e.g., updating per-shop records, or invoking a differently-privileged handler such as `app/uninstalled`) is not the value the cryptographic signature actually protects.

### Impact Explanation
This breaks the tenant isolation the HMAC check is documented to provide. Any application that uses `data.shop` from `WebhookMetadata` to key per-tenant data updates (exactly the pattern shown in the gem's own docs, `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be tricked into writing/executing webhook data under the identity of a shop the attacker does not control, i.e., cross-tenant data confusion/injection. An attacker can also relabel the `topic` header to force a captured body into a different handler than the one Shopify actually intended, potentially reaching more sensitive webhook handlers (e.g. billing, uninstall, GDPR) with attacker-influenced (though not attacker-forged from scratch) routing. This lands squarely in the "cross-tenant access" Critical impact category defined by the rules.

### Likelihood Explanation
Exploitation requires no privileged credentials: the webhook endpoint is a public, unauthenticated HTTP route by design (`docs/usage/webhooks.md` shows a bare Rails controller action) [9](#0-8) . Obtaining one valid `(raw_body, hmac)` pair only requires installing the app on any shop (a normal, unprivileged action for any merchant) and capturing the webhook Shopify sends to that shop's own endpoint — no access to `api_secret_key` itself is needed. The rest of the attack is a simple header rewrite and a direct POST.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, and ideally `webhook_id`) in the signed material verified by `HmacValidator`, or otherwise independently authenticate them (e.g., verify `shop` against the shop associated with a stored, previously-registered webhook subscription/session before dispatch). At minimum, `Registry.process` should not treat `request.shop`/`request.topic` as trusted merely because *an* HMAC over the body validated — the specific shop and topic claimed by the headers must themselves be covered by the signature.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; capture a legitimately delivered webhook, e.g. for `orders/create`:
   - `raw_body = '{"id":1,...}'`
   - `X-Shopify-Hmac-Sha256: <valid hmac over raw_body signed with the app's shared api_secret_key>`
2. Replay the exact same `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's public webhook endpoint, but set:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: app/uninstalled` (or any other registered topic)
3. `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the shared secret [6](#0-5) .
4. `Registry.process` looks up the handler for the spoofed `app/uninstalled` topic and invokes it with `WebhookMetadata.new(topic: "app/uninstalled", shop: "victim-shop.myshopify.com", body: <attacker's captured body>, ...)` [10](#0-9) , causing the host application to act on the victim shop's identity using attacker-supplied data/topic routing.

### Citations

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

**File:** docs/usage/webhooks.md (L127-135)
```markdown
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
