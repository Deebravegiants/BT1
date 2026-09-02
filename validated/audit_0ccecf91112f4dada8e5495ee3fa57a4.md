Confirmed. The docs at `docs/usage/webhooks.md:125` explicitly state that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify," and the handler example at line 26 directly trusts `data.shop` as the tenant identity (`shop_domain: data.shop`) for downstream processing — but the `shop` field is never covered by the HMAC.

### Title
Webhook `shop`/`topic` identity fields are not covered by HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read from HTTP headers that are excluded from the HMAC computation. `ShopifyAPI::Webhooks::Registry.process` validates only that this body-only HMAC is correct, then passes the unauthenticated `shop`/`topic` header values straight to the host application's webhook handler as trusted tenant identity.

### Finding Description
`Utils::HmacValidator.validate` computes the expected signature from `verifiable_query.to_signable_string` and compares it to the `hmac` field [1](#0-0) . For webhook requests, `to_signable_string` returns only `@raw_body`, and `hmac`, `shop`, `topic`, `api_version`, and `webhook_id` are all pulled from separate, unsigned HTTP headers [2](#0-1) .

`Registry.process` validates the HMAC and then constructs `WebhookMetadata` directly from these unauthenticated header values, handing `request.shop` and `request.topic` to the app's handler as if they were verified [3](#0-2) .

The identity binding that should hold is: `hmac_signature == HMAC(secret, shop || topic || body)`. In this implementation it is actually `hmac_signature == HMAC(secret, body)`, so `shop` and `topic` are "verified" only in the sense that *some* request from *some* installed shop with that exact body produced a valid signature — the signature says nothing about which shop or topic it was for.

Because the app's client secret (used to compute the HMAC) is shared across every merchant installation of the app, and Shopify commonly sends identical or predictable JSON bodies for different shops/topics (e.g., empty bodies `{}`, or bodies with easily-guessable/observable fields), a party who has ever received one legitimate webhook (e.g., for their own store's installation) can capture the `raw_body` + valid `hmac`, then replay it to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at a different merchant's shop, or a forged `X-Shopify-Topic` header. `HmacValidator.validate` will still return `true`, because it never inspects those headers, and the handler will process the payload as if it genuinely originated from the spoofed shop/topic.

### Impact Explanation
This breaks the tenant boundary the HMAC check is documented to enforce: `docs/usage/webhooks.md` states `Registry.process` "will verify the request did indeed come from Shopify" and its own example handler forwards `data.shop` downstream as the shop identity for job processing [4](#0-3) . A host app relying on this guarantee (which is exactly what the gem's own documentation encourages) can be made to attribute webhook data to the wrong merchant, update the wrong shop's local records, trigger side effects (job enqueuing, notifications, order/inventory sync) under the wrong tenant, or bypass per-shop authorization checks that key off `data.shop`. This is a cross-tenant integrity issue reachable by any unprivileged party who has observed one valid webhook body/HMAC pair for the app (e.g., their own installed shop), without needing the `client_secret`, an access token, or any privileged account.

### Likelihood Explanation
Likelihood is elevated by two facts: (1) many webhook topics produce identical or near-identical bodies across shops (e.g., filtered/empty payloads, or bodies containing only non-identifying fields), making capture-and-replay straightforward for anyone who can install the app on a test/dev shop; and (2) the vulnerability requires no credentials beyond having received one legitimate webhook, which any merchant/developer with the app installed can do trivially and legally.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, and ideally `webhook_id`/`api_version`) in the signed payload used for HMAC verification, or otherwise cryptographically bind them to the signature (e.g., verify `shop` against the caller of `Registry.register`/an allow-list of shops with active sessions, and include `topic`+`shop` in `to_signable_string`). At minimum, document that `data.shop` and `data.topic` are not authenticated by the HMAC check and must be independently validated by the host application before being trusted as tenant identity.

### Proof of Concept
1. App installs on `shop-a.myshopify.com` and receives a legitimate webhook for topic `orders/create` with body `{}` (a body Shopify sends for filtered/empty-field webhooks) and a valid `X-Shopify-Hmac-Sha256` header computed as `HMAC-SHA256(client_secret, "{}")`.
2. Attacker (who controls `shop-a`, or has otherwise observed this body/HMAC pair) POSTs to the same app's public webhook endpoint with:
   - `X-Shopify-Topic: orders/create`
   - `X-Shopify-Shop-Domain: shop-b.myshopify.com` (a victim shop, spoofed)
   - `X-Shopify-Hmac-Sha256: <the same valid HMAC>`
   - body: `{}`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which computes `HMAC(client_secret, "{}")` and matches the supplied header — validation passes [5](#0-4) .
4. The handler receives `WebhookMetadata.new(shop: "shop-b.myshopify.com", topic: "orders/create", ...)` and processes it as if it were a genuine event for `shop-b`, even though `shop-b` never sent this webhook [6](#0-5) .

### Citations

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

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

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
```
