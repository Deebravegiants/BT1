## Finding

### Title
Webhook shop/topic identity fields are trusted from unauthenticated headers while only the raw body is HMAC-verified, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC that `Utils::HmacValidator` checks in `Webhooks::Registry.process` proves nothing about the `shop`, `topic`, `webhook_id`, or `api_version` values, all of which are read straight from HTTP headers and handed to the app's business-logic handler as trusted, verified data.

### Finding Description
`Registry.process` treats a passing HMAC check as proof the whole request "did indeed come from Shopify" (per `docs/usage/webhooks.md` line 125) and then builds `WebhookMetadata` directly from header values: [1](#0-0) 

But the cryptographic binding only covers the body: [2](#0-1) 

`hmac` is computed over `@raw_body` only (`to_signable_string` returns `@raw_body`), while `shop`, `topic`, `webhook_id`, and `api_version` are pulled from `shopify_header(...)` — plain HTTP header lookups with no signature coverage. `HmacValidator.validate_signature` then compares only against the signable string (the body): [3](#0-2) 

The identity binding that should hold is: `hmac == HMAC(secret, body ‖ shop ‖ topic)`, but the actual check is `hmac == HMAC(secret, body)`. Since the app's `api_secret_key` is shared across every shop that installs the app (it is the app's client secret, not a per-shop secret), any tenant that legitimately triggers a webhook for their own store obtains a `(body, hmac)` pair that is valid for that same secret regardless of which shop it nominally belongs to. That pair can then be replayed to the app's webhook endpoint with a different `X-Shopify-Shop-Domain` / `X-Shopify-Topic` header, and `Registry.process` will accept it (HMAC check passes because it never inspected those headers) and dispatch it to the handler as if it originated from a different shop/topic, exactly matching the documented usage pattern that keys business logic off `data.shop`: [4](#0-3) 

### Impact Explanation
This breaks the identity binding `shop-in-signed-payload == shop-used-for-tenant-dispatch`. Because the header-declared shop is never bound to the HMAC, a malicious but legitimately-onboarded tenant (an "unprivileged" party relative to *other* merchants of the same multi-tenant app) can forge webhook events attributed to another shop, or relabel one topic as another, causing the app to execute tenant-scoped business logic (data updates, order processing, uninstall/GDPR handling, etc.) against the wrong tenant's records — a cross-tenant access impact.

### Likelihood Explanation
Exploitation requires the attacker to be able to trigger at least one genuine webhook delivery for a shop they control (trivial — install the app on any test store and cause an event), capture the `(raw_body, X-Shopify-Hmac-Sha256)` pair, and resend it to the app's public webhook endpoint with modified `X-Shopify-Shop-Domain`/`X-Shopify-Topic` headers. No access token, `api_secret_key`, or privileged credential is needed; the shared app secret is never disclosed to the attacker, only reused implicitly via the replayed HMAC.

### Recommendation
Bind the identity fields into the signed material instead of trusting headers unconditionally: include `shop`, `topic`, and `webhook_id` in the value that is HMAC-verified (or, since Shopify's `X-Shopify-Hmac-Sha256` only covers the body by protocol design, require callers to cross-check `request.shop` against a shop that is already known/active in the app's own session store before dispatching to the handler, and to enforce webhook-id uniqueness so a replayed body/hmac pair cannot be reprocessed under a different shop/topic label).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers an event (e.g., `orders/create`) so Shopify sends a legitimate webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H = HMAC(secret, B)`.
2. Attacker captures `B` and `H` (e.g., via their own logging proxy, browser devtools on a tunnel they control, or by owning the receiving infra for their own store's test webhook).
3. Attacker (or any actor who can reach the app's public webhook route) sends a new HTTP request to the same endpoint with the same body `B` and the same `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and/or a different `X-Shopify-Topic`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes `HMAC(secret, B)` and compares to `H` — it matches, since `B` and `H` are unchanged.
5. `Registry.process` proceeds to call `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` using the attacker-forged `shop`/`topic` headers, causing the app to process the event as belonging to `victim-shop.myshopify.com` instead of the attacker's own shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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
