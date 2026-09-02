This confirms the vulnerability. The webhook `hmac` in `ShopifyAPI::Webhooks::Request#to_signable_string` is computed only over `@raw_body`, and `topic`/`shop`/`webhook_id`/`api_version` are all pulled directly from unauthenticated HTTP headers, entirely outside the HMAC's coverage.### Title
Webhook shop/topic attribution trusted from unauthenticated headers while HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, but the `shop`, `topic`, `webhook_id`, and `api_version` values that the app's handler receives and acts on are read directly from HTTP headers that are never included in that HMAC computation. This breaks the intended binding: `HMAC(body) valid` should imply `shop header == shop that produced this HMAC`, but the gem never enforces that equality.

### Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against `verifiable_query.hmac`. [1](#0-0) 

For webhooks, `ShopifyAPI::Webhooks::Request` implements `VerifiableQuery` such that:
- `hmac` is read from the `x-shopify-hmac-sha256` (or `shopify-hmac-sha256`) header.
- `to_signable_string` returns **only** `@raw_body`.
- `shop`, `topic`, `webhook_id`, and `api_version` are all read from other, completely unauthenticated headers (`x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, `x-shopify-api-version`). [2](#0-1) 

`Registry.process` then validates the HMAC of the body only, and immediately trusts `request.shop`/`request.topic` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

Because the signature only binds the JSON body bytes, and the shop-domain/topic/webhook-id headers are not part of the signed material, the equality the system needs — "the shop whose secret produced this HMAC" == "the shop header value delivered to the handler" — is never checked. Any valid `(raw_body, hmac)` pair (for example, one legitimately obtained from a webhook fired for the attacker's own installed shop, which shares the same `api_secret_key` for a given app) will pass `HmacValidator.validate` regardless of what `x-shopify-shop-domain`/`x-shopify-topic` values accompany it, because those headers are never fed into `to_signable_string`.

### Impact Explanation
This is a cross-tenant confusion vector at the boundary between the gem's authentication check and the trust decisions made by the host app: `Registry.process` hands the handler a `WebhookMetadata.shop` value that was never authenticated, while the only thing actually verified is that *some* shop using this app's secret produced that raw body. Per the documented usage pattern, apps process `data.shop` to route work (e.g., load the shop's session, dispatch a background job "for" that shop, or persist data keyed by `data.shop`), as shown in the gem's own docs. [4](#0-3) 

An attacker who controls a shop installed on the same app (a routine, unprivileged position for any developer/merchant who installs a public app) can capture a legitimately-signed `(body, hmac)` pair from their own shop's webhook deliveries and replay it to the app's webhook endpoint with a forged `x-shopify-shop-domain` header naming a victim shop. Since the HMAC check never inspects that header, the request passes verification, and the handler receives `WebhookMetadata` falsely attributing the (attacker-controlled) body/topic to the victim shop — leading the host app to act on another tenant's identity (cross-tenant data confusion/injection).

### Likelihood Explanation
Moderate-to-high: exploitation requires only an unprivileged position as an installed shop of the target app (a `client_secret` is not needed — only a valid webhook delivery to the attacker's own shop, which the attacker legitimately receives), plus the ability to POST arbitrary headers/body to the app's public webhook callback URL, which by design must be internet-reachable. No TLS interception, leaked credentials, or privileged account is required.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string used for webhook HMAC verification (mirroring how `Oauth::AuthQuery#to_signable_string` binds `shop`, `host`, `code`, `state`, `timestamp` into the OAuth HMAC), or otherwise cryptographically bind these header values before they are handed to the webhook handler, so that `HmacValidator.validate` fails whenever the attacker-controlled headers don't match the shop/topic that legitimately produced the signature.

### Proof of Concept
1. App AppX is installed on both `attacker-shop.myshopify.com` and `victim-shop.myshopify.com` (public app, unprivileged installs).
2. Attacker triggers/waits for a webhook delivery to their own shop, capturing the raw POST: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid because `H = HMAC-SHA256(api_secret_key, B)`), and headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`.
3. Attacker resends the exact same `raw_body = B` and `x-shopify-hmac-sha256: H` to AppX's public webhook endpoint, but rewrites `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#to_signable_string` returns `B` (unchanged); `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(api_secret_key, B) == H` → **true**, since the shop header is never part of the signed data. [2](#0-1) [5](#0-4) 
5. `Registry.process` passes verification and invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: parsed(B), ...)`, causing the host app to process attacker-controlled data under the victim shop's identity. [6](#0-5)

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
