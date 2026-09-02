Confirmed: `Context.api_secret_key` is a single global secret configured once for the entire app (not per-shop), stored at `lib/shopify_api/context.rb:8,79` and used identically for every merchant/tenant. This confirms the cross-tenant forgery is exploitable, since the same HMAC key is used to validate webhooks from every shop.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/utils/hmac_validator.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, and `webhook-id` are read directly from unauthenticated headers. `HmacValidator.validate` verifies the HMAC exclusively against that body using the app's single, shop-independent `Context.api_secret_key`. Any entity capable of generating a genuinely-signed webhook for *any* shop it controls (e.g., its own dev/trial store on the same app) can replay that valid `(body, hmac)` pair while substituting the `x-shopify-shop-domain` header for an arbitrary victim shop, and the signature will still validate.

### Finding Description
The binding that should hold is:
`hmac == HMAC(secret, body || shop || topic || webhook_id)`

but the actual implementation only enforces:
`hmac == HMAC(secret, body)`

with `shop` (and `topic`, `webhook_id`) excluded from the signed material: [1](#0-0) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`: [2](#0-1) 

`Registry.process` then trusts `request.shop` — sourced straight from the unauthenticated header — to build the metadata handed to the app's webhook handler, without any additional binding to the signed body: [3](#0-2) 

Because `Context.api_secret_key` is one single value shared by the whole app across every installed shop (it is set once via `Context.setup` and not scoped per-tenant): [4](#0-3) [5](#0-4) 

an attacker who has installed the app on their own shop (an ordinary, unprivileged action available to any Shopify user/merchant, and thus "unprivileged-internet-user" reachable) can trigger a real webhook delivery with attacker-chosen body content, capture the genuine `(raw_body, x-shopify-hmac-sha256)` pair issued by Shopify for their own shop, and then submit that exact pair to the app's webhook endpoint while changing only the `x-shopify-shop-domain` header to a victim shop's domain. `HmacValidator.validate` will pass because it never inspects the header, and `Registry.process` will hand the handler `WebhookMetadata` claiming the data originated from the victim shop.

### Impact Explanation
This breaks the tenant-identity binding that host applications rely on: `shop` returned by `ShopifyAPI::Webhooks::Request` is treated by consuming apps as an authenticated identifier of which merchant/tenant the payload belongs to (this is the documented purpose of the field, per `docs/usage/webhooks.md` and the `WebhookMetadata#shop` accessor used in handlers). Forging it allows an attacker to inject or overwrite data attributed to a victim shop's tenant record in the host application (e.g., fake `orders/create`, `app/uninstalled`, GDPR, or fulfillment events), which is a cross-tenant data integrity/confidentiality violation qualifying as Critical - cross-tenant access.

### Likelihood Explanation
Likelihood is high: the only prerequisite is the attacker's own legitimate installation of the app (installing an app on one's own development or trial store is a normal, unprivileged action, not a compromise of any credential). No access token, `client_secret`, or victim credential is required — only observation of one genuine webhook delivery to the attacker's own shop and replaying it with a modified header.

### Recommendation
Bind the tenant/shop identity (and topic/webhook id, if used for routing) into the signed material, or independently verify that the `shop` header value corresponds to a session/shop the app has actually installed/expects for that specific delivery before trusting it in `WebhookMetadata`. At minimum, document and enforce that `request.shop` must never be used as an authenticated tenant identifier without cross-checking it against Shopify's registered webhook subscription/shop for that specific installation.

### Proof of Concept
1. App developer installs their app on `attacker.myshopify.com` (their own shop) and registers a webhook, e.g. `orders/create`.
2. Trigger the event on `attacker.myshopify.com` so Shopify sends a real webhook: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`, `x-shopify-shop-domain: attacker.myshopify.com`.
3. Capture this exact `(B, hmac)` pair.
4. Replay a forged HTTP POST to the app's webhook endpoint with the same `raw_body = B` and same `x-shopify-hmac-sha256` header, but set `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate` at [6](#0-5)  succeeds because it only checks `B` against `secret`.
6. `ShopifyAPI::Webhooks::Registry.process` at [7](#0-6)  invokes the app's handler with `shop: "victim.myshopify.com"`, even though the payload never actually originated from Shopify on behalf of that shop.

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

**File:** lib/shopify_api/context.rb (L8-9)
```ruby
    @api_key = T.let("", String)
    @api_secret_key = T.let("", String)
```

**File:** lib/shopify_api/context.rb (L78-79)
```ruby
        @api_key = api_key
        @api_secret_key = api_secret_key
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
