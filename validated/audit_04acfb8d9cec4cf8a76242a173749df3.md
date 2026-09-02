This confirms the finding. `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `#topic`, `#shop`, `#api_version`, and `#webhook_id` are read directly from HTTP headers that are never included in the HMAC-signed material [2](#0-1) . `Registry.process` only validates the body HMAC via `Utils::HmacValidator.validate(request)` and then dispatches the handler using `request.shop` taken straight from the unsigned header [3](#0-2) . Since Shopify signs webhooks with the single shared `api_secret_key` for the whole app (identical secret for every installed shop) as shown in `HmacValidator.validate_signature`, which computes the HMAC purely from `to_signable_string` [4](#0-3) , this is a genuine identity-binding gap matching the requested bug class.

### Title
Webhook shop attribution is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, but the `shop`, `topic`, `api_version`, and `webhook_id` values used by `Registry.process` to route and attribute the webhook are read from HTTP headers that are never covered by that signature. Because Shopify signs every webhook for an app with the same shared `api_secret_key` regardless of which shop sent it, any merchant who installs the app can capture a validly-signed webhook delivered to their own endpoint and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header rewritten to a victim shop, while the HMAC still validates.

### Finding Description
The intended identity binding is: `hmac_valid(body) == true` should imply `(shop, topic, body)` as processed by the app is the exact tuple Shopify actually signed and sent. Instead the code only proves `hmac_valid(body) == true`; `shop`/`topic`/`webhook_id`/`api_version` are unauthenticated metadata pulled from headers with no cryptographic tie to the body or to each other.

- `Request#to_signable_string` returns `@raw_body` and nothing else: [1](#0-0) 
- `Request#shop`, `#topic`, `#webhook_id`, `#api_version` come straight from headers, with no relation to the signed body: [2](#0-1) 
- `Registry.process` gates only on the body HMAC, then immediately trusts `request.shop`/`request.topic` for dispatch and handler payload construction: [3](#0-2) 
- `HmacValidator.validate` / `validate_signature` compute and compare the HMAC solely against `verifiable_query.to_signable_string`, i.e., the body: [4](#0-3) 

Because the same `api_secret_key` is used to sign webhooks for every shop that has installed a given app, an attacker who installs the app on their own store (an unprivileged action requiring no special credentials) legitimately receives webhooks with valid `X-Shopify-Hmac-Sha256` values for arbitrary attacker-chosen event bodies (e.g. by triggering `orders/create`, `customers/data_request`, etc. on their own store). The attacker can then replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header of a different, victim shop. `HmacValidator.validate` still returns `true` because it never inspects the shop header, and `Registry.process` builds `WebhookMetadata` and invokes the handler with `shop: request.shop` set to the victim's domain [5](#0-4) .

For a multi-tenant host application that keys per-shop state, data records, or GDPR/redact processing off of `data.shop` from `WebhookMetadata`, this lets one tenant inject fabricated, cryptographically "valid" events attributed to another tenant — a cross-tenant boundary violation performed entirely through this gem's own webhook verification API.

### Impact Explanation
This meets the Critical bar of cross-tenant access: an unprivileged attacker (any merchant who can install the target app) can make the app process a forged event as if it originated from a shop they do not own or control, without needing the app's `client_secret`, any access token, or any privileged account — they only need their own legitimately-issued webhook traffic and the ability to send an HTTP request to the app's public webhook endpoint with a modified header.

### Likelihood Explanation
High. Installing an app to receive real webhook traffic is a normal, unprivileged action for any Shopify merchant. Capturing your own webhook's raw body + `X-Shopify-Hmac-Sha256` and replaying it with a different `X-Shopify-Shop-Domain` header requires no special tooling — just control of the HTTP request sent to the webhook endpoint (e.g. via `curl`), since this gem's `HmacValidator` never binds the header value into the signed string.

### Recommendation
Do not treat `shop`/`topic`/`webhook_id`/`api_version` headers as trusted once HMAC validation on the body passes. Either:
1. Include these header values inside `to_signable_string` in a canonical, unambiguous encoding so the HMAC covers the full tuple `(shop, topic, api_version, webhook_id, body)`, or
2. Require callers to cross-check `request.shop` against an independently known, previously stored shop for the session/access token being used to process that webhook before dispatching to a handler, and document that `Registry.process` alone does not authenticate the shop attribution.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a normal, unprivileged install).
2. Attacker triggers a webhook delivery (e.g., updates an order) and captures the raw HTTP request Shopify sends to the app's webhook endpoint, including `X-Shopify-Hmac-Sha256: <valid_hmac>` and body `B`.
3. Attacker (or any user with network access to the app's public webhook endpoint) resends the exact same request, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. In the app:
   ```ruby
   request = ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {
     "x-shopify-topic" => "orders/updated",
     "x-shopify-hmac-sha256" => valid_hmac_from_step_2,
     "x-shopify-shop-domain" => "victim-shop.myshopify.com",
   })
   ShopifyAPI::Webhooks::Registry.process(request) # does not raise; handler runs with shop == "victim-shop.myshopify.com"
   ```
5. `Utils::HmacValidator.validate(request)` returns `true` (it only checks `B` against the shared secret), and the registered handler executes with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the event never originated from that shop.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
