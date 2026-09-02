Confirmed: `WebhookMetadata.shop` is populated directly from `request.shop` [1](#0-0) , and `request.shop` is parsed only from the `x-shopify-shop-domain` header, which is not part of the HMAC-signed payload [2](#0-1) .

### Title
Webhook shop-domain identity not bound by HMAC allows cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop` value taken from the unauthenticated `x-shopify-shop-domain` header when dispatching to the app's handler. The shop identity is never included in the HMAC-covered bytes, so a party who can obtain one validly-signed webhook body (e.g. a merchant using the app's own store, or any leaked/replayed webhook payload) can resubmit that same body with a different `shop-domain` header value and have the host application process it as if it originated from a different tenant.

### Finding Description
`Registry.process` performs authentication as:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [3](#0-2) 

`HmacValidator.validate` computes/compares the HMAC against `verifiable_query.to_signable_string` [4](#0-3) , and for `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [5](#0-4) . Meanwhile `shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header without any cryptographic binding to the body or its HMAC [2](#0-1) .

The equality this breaks is: **shop authenticated by HMAC == shop acted upon**. Before the request: the HMAC only proves "this body was signed by the app's `api_secret_key`" (which is shared across every merchant that installed the app, since Shopify computes webhook HMACs using the app's client secret, not a per-shop secret). After the request: the gem passes `request.shop` — taken from an attacker-controllable header — into `WebhookMetadata`, which the host application uses to key its per-tenant business logic (e.g. `handle(data:)` in `WebhookHandler` and any app implementation keyed on `data.shop` [6](#0-5) ). Since the shop field is never part of the signed bytes, HMAC validity for one shop's webhook body says nothing about which shop the body actually belongs to.

### Impact Explanation
Any unprivileged user who can install the app on their own store (a normal, unprivileged onboarding flow) can trigger webhook deliveries with attacker-chosen body content (e.g. by editing an order/customer/product on their own store to shape the JSON body), capture the resulting valid `(raw_body, hmac)` pair, and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `Registry.process` will accept it as authentic and hand the attacker-chosen body to the handler tagged as belonging to the victim shop. Depending on how the host application uses `data.shop`/`data.body` (e.g., updating per-shop cached state, triggering fulfillment actions, billing, or metafield writes scoped by shop), this results in cross-tenant data corruption/injection — a violation of the tenant isolation the gem is supposed to guarantee for webhook processing.

### Likelihood Explanation
Likelihood is realistic: the attacker only needs the ability to install the app on their own account (any merchant can do this) and to send an HTTP POST with custom headers to the app's public webhook endpoint — both are unprivileged-internet-user actions requiring no access token, secret, or social engineering.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-covered signable string, or otherwise cryptographically bind the header-derived `shop` value to the signed payload before trusting it in `WebhookMetadata`. At minimum, `Webhooks::Request#to_signable_string` should incorporate `shop`, and `HmacValidator` (or `Registry.process`) should reject requests where the header-derived shop was not part of what was verified.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger a webhook event (e.g. `orders/create`) with a body crafted by the attacker.
2. Shopify sends the webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`.
3. Attacker captures `raw_body` and `x-shopify-hmac-sha256`.
4. Attacker POSTs the identical `raw_body` and `x-shopify-hmac-sha256` to the same endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC [5](#0-4) ; `Registry.process` calls the handler with `shop: "victim.myshopify.com"` [1](#0-0) , causing the app to process attacker-controlled data as belonging to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L189-199)
```ruby
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-31)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
