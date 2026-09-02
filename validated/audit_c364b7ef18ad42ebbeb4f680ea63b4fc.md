### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing shop-spoofing / cross-tenant webhook injection - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authenticated for a given shop as soon as `Utils::HmacValidator.validate` passes, but the HMAC is computed only over the raw request body — never over the `x-shopify-shop-domain` (or `shopify-shop-domain`) header that is later handed to the app as the authoritative tenant identifier. This breaks the intended binding `hmac_verified_bytes == tenant_identity_used_by_handler`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop` is read straight from an unauthenticated header with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` only ever verifies `verifiable_query.to_signable_string` (the body) against the `hmac` field — it never touches `shop`: [3](#0-2) 

`Registry.process` performs exactly this check and then immediately forwards the unauthenticated `request.shop` to the app-provided handler as the trusted tenant identifier: [4](#0-3) 

The documented usage explicitly instructs developers to trust `data.shop` as "the shop domain of the webhook" and use it directly for tenant-scoped side effects (e.g. `shop_domain: data.shop`): [5](#0-4) 

Since `api_secret_key` (`client_secret`) is shared across every shop that has installed a given app, any merchant that has installed the app can obtain a valid `(raw_body, hmac)` pair for their own shop (either from a real Shopify-delivered webhook, or by computing it themselves if they can trigger any webhook-eligible event). They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim `x-shopify-shop-domain` value. The gem's `HmacValidator` will report the request as valid — because it never inspected `shop` — and `Registry.process` will call the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

This is the "field acted on but not covered by the HMAC" analog of the referenced report's identity-binding failure: just as the Audius bug enforced `minDelegationAmount` on the wrong aggregate (across all providers instead of per-provider), this gem enforces authenticity on the wrong scope (the body only, instead of the tenant-identifying header), so the security check answers "yes, authentic" for a value it never validated.

### Impact Explanation
This qualifies as **cross-tenant access** under the Critical bucket: an attacker who is a legitimate but unprivileged user of the shared multi-tenant app (an installed merchant, not requiring `api_secret_key`, an access token, or any privileged credential) can inject events, or exfiltrate/replay data, attributed to a different merchant's tenant context. Any host application following the documented pattern of keying tenant-scoped work (session lookup, DB writes, job enqueue) off `data.shop` is directly exposed, since that is exactly the documented, non-misuse usage shown in `docs/usage/webhooks.md`.

### Likelihood Explanation
Likelihood is realistic for any app with more than one installed shop: the attacker only needs their own legitimate install (any unprivileged internet user who installs the app) to obtain a valid `(body, hmac)` pair signed with the shared `api_secret_key`, then send a forged HTTP request with a different `shop-domain` header value — no secret material or victim-side access is required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the signed payload verification, or otherwise cryptographically bind the claimed shop to the HMAC-verified bytes before it is handed to the handler — e.g., verify that the resolved `shop` corresponds to a shop with an active, previously-established registration/session for this app, rather than trusting the raw header value once the body HMAC checks out.

### Proof of Concept
1. App "MyApp" is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com` (both share the same `api_secret_key`).
2. Attacker triggers (or fabricates, since they only need a valid body+HMAC pair for *any* body content they choose to send, as `HmacValidator` accepts any body as long as `hmac == HMAC_SHA256(secret, body)`) a request:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of body under shared api_secret_key>
   x-shopify-shop-domain: victim-shop.myshopify.com   # forged
   x-shopify-webhook-id: attacker-chosen
   { ...attacker-controlled body... }
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which passes because it only checks the body against the HMAC.
4. `WebhookHandler#handle` receives `data.shop == "victim-shop.myshopify.com"` and performs tenant-scoped work (per the documented pattern) as if the event genuinely originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
