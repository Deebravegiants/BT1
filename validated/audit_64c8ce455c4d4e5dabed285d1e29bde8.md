### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that is read directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but `Utils::HmacValidator.validate` only ever verifies the raw request body against the app's `api_secret_key`. The tenant-identifying value (`shop`) is never part of the signed content, so the equality the app relies on — *"HMAC-authenticated request == request.shop is the true origin shop"* — does not hold.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string`: [2](#0-1) 

`Registry.process` treats a passing HMAC check as full authentication of the request and then forwards `request.shop` (taken straight from the header, never covered by the signature) to the application handler as an authenticated tenant identifier: [3](#0-2) 

Because `shop`, `topic`, `webhook_id`, and `api_version` are all sourced from headers that are excluded from `to_signable_string`, any request whose *body* carries a valid HMAC for the app's secret will pass `HmacValidator.validate`, regardless of what shop-domain header accompanies it. An attacker who controls a shop that is installed on the same app (a normal, unprivileged capability — any developer/merchant can install a public app on their own store) can trigger a webhook for their own shop, capture the resulting `raw_body` + valid `hmac-sha256` value, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Registry.process` will accept it as valid and hand the handler `WebhookMetadata#shop == victim_shop` alongside attacker-controlled `body` content.

### Impact Explanation
Apps built on this gem are documented to treat `data.shop` from `WebhookMetadata` as the authoritative tenant for the event (e.g., to look up the victim's stored access token and perform actions, or to key data ingestion per shop): [4](#0-3) 

Since `shop` is never bound to the signature, an attacker can inject attacker-controlled body content that the host app will process under a victim shop's identity/session — a cross-tenant confusion primitive purely through the library's own webhook-verification contract (`HmacValidator.validate` + `Request#shop`), not through host-application misuse of an undocumented feature.

### Likelihood Explanation
Exploitation only requires the ability to install the target app on an attacker-owned store (a standard, unprivileged action for any public/custom Shopify app) to obtain one legitimately-signed `(raw_body, hmac)` pair, plus the ability to POST to the app's public webhook endpoint with a forged shop header — no `api_secret_key`, access token, or privileged account is needed.

### Recommendation
Bind the shop domain (and ideally topic/webhook id) into the signed material verified by `HmacValidator`, or independently authenticate/authorize the `shop` header against a shop the app has an active, previously-established session/install for before trusting `WebhookMetadata#shop`. Document clearly that `request.shop`/`data.shop` is not covered by the HMAC and must not be used as the sole tenant-authorization signal.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`), capturing the exact `raw_body` and the resulting `x-shopify-hmac-sha256` value (both public to the attacker as the shop owner).
2. Attacker sends a POST to the app's webhook endpoint with:
   - `raw_body` = the captured body (attacker fully controls this content since it originated from their own store)
   - `x-shopify-hmac-sha256` = the captured, still-valid HMAC
   - `x-shopify-shop-domain` = `victim.myshopify.com`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the secret (`lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. The registered handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled JSON>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`) and processes attacker data under the victim's tenant context.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```
