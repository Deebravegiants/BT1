Confirmed: the gem's own documentation (`docs/usage/webhooks.md:125`) explicitly states that `Registry.process` "will verify the request did indeed come from Shopify" and hands the caller `data.shop` (`docs/usage/webhooks.md:14`, `:26`) as the trusted tenant identifier to key application logic (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`). The gem itself computes and asserts this guarantee via `Utils::HmacValidator.validate(request)` inside `Registry.process`, so the binding failure is rooted in this gem's own code, not merely a downstream misuse of an undocumented API.

### Title
Webhook shop-domain (tenant identity) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authenticated once `Utils::HmacValidator.validate(request)` passes, and then forwards `request.shop` to the app's handler as the trusted tenant identifier. However, `Webhooks::Request#to_signable_string` returns only the raw body — the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are excluded from the HMAC computation. Because the app's `client_secret`/`api_secret_key` is shared across every shop that installs the app, a genuine, validly-signed webhook body received for one (attacker-controlled) shop can be re-submitted to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop. The signature still validates (it only signs the body), so the handler executes believing the event originated from the victim shop, breaking the identity binding `HMAC-covered bytes == data acted upon`.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw request body: [2](#0-1) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all parsed from HTTP headers that sit entirely outside that signed string: [3](#0-2) 

`Registry.process` gates the whole operation on this single HMAC check, then passes the unauthenticated `request.shop` straight to the app-defined handler as the tenant identity: [4](#0-3) 

This contrasts with the OAuth `AuthQuery`, in this same gem, where `shop` **is** included inside the signed string, correctly binding the shop to the HMAC: [5](#0-4) 

The gem's own documentation instructs apps to trust `data.shop` from a processed webhook as the tenant key for downstream logic: [6](#0-5) 

**Attack path (no privileged credentials required):** An unprivileged attacker installs the target app on their own (attacker-controlled) shop — a normal, unprivileged action any Shopify merchant can take. Shopify will legitimately send the attacker webhooks for their own shop's events, each with a valid `x-shopify-hmac-sha256` computed with the app's single, shared `api_secret_key`. Since the signature covers only the body (not the `shop-domain` header), the attacker can replay that exact body + HMAC pair to the app's webhook endpoint while substituting `x-shopify-shop-domain` (and, if desired, `x-shopify-webhook-id`) to name a victim shop that also has the app installed. `HmacValidator.validate` still succeeds because the body bytes and secret are unchanged, so `Registry.process` invokes the handler with `WebhookMetadata.shop` set to the victim's domain even though the payload content actually originated from the attacker's own shop.

This breaks the identity equality the gem is supposed to enforce:
`bytes covered by the HMAC == bytes the handler treats as authenticated (shop + topic + body)`
Here, only `body` is covered, while `shop` (the tenant boundary) is not, letting the attacker set the tenant label independently of the signed content.

### Impact Explanation
This is a cross-tenant data-injection/confusion primitive: an attacker who legitimately installs the app on their own shop can cause the app to process arbitrary (attacker-crafted, since they control their own shop's data/content that generates the webhook body) event data under a victim shop's identity. Typical handler logic (as shown in the gem's own doc example, `shop_domain: data.shop`) uses this shop value to look up per-tenant sessions/records and write or trigger business logic keyed to that shop — enabling cross-tenant data corruption or state confusion without possessing the victim's access token, session, or the app's `client_secret`. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that (a) allows public/self-serve installation (so the attacker can obtain their own valid, app-signed webhook traffic) and (b) uses `data.shop` from `WebhookMetadata` as a trust anchor for tenant-scoped operations, which is exactly the pattern the gem's documentation recommends. No secret material beyond what an ordinary merchant installer already has access to (their own webhook payloads) is required, and the required header substitution is a simple HTTP replay.

### Recommendation
Bind the tenant-identifying and topic-identifying headers into the signed material, or otherwise cryptographically tie them to the payload before trusting them:
- Include `shop`, `topic`, `webhook_id`, and `api_version` in `Webhooks::Request#to_signable_string` (mirroring how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop`), and update `HmacValidator` usage accordingly; or
- At minimum, document prominently that `WebhookMetadata.shop`/`topic`/`webhook_id` are **not** covered by the HMAC and must not be trusted as tenant identifiers by themselves — instead, apps must independently verify the shop against an out-of-band registered webhook ID/topic mapping.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` (unprivileged self-service action).
2. Shopify sends a legitimate webhook, e.g. for `orders/create`, to the app's registered endpoint with headers:
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC over raw body, computed with the app's shared api_secret_key>`
   - `x-shopify-topic: orders/create`
3. Attacker captures this raw request (body + signature) — trivial since it is delivered to an endpoint the attacker controls (their own webhook endpoint on the same shared app), or they configure their own reverse proxy to capture it.
4. Attacker resends the exact same body and `x-shopify-hmac-sha256` value to the app's webhook controller, but with `x-shopify-shop-domain` changed to `victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it validates only `@raw_body`: [7](#0-6) 
6. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: <attacker's content>, ...)`: [8](#0-7) 
7. The app's handler processes the attacker-supplied body as though it were a genuine event from `victim.myshopify.com`, per the documented handler pattern (`shop_domain: data.shop`), demonstrating cross-tenant injection without any credential belonging to the victim or the app's `client_secret`.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
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
