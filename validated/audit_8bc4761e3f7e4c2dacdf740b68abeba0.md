### Title
Webhook `shop` field is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" before invoking the app's webhook handler with the `shop` value taken from the request. In reality, the HMAC signature only covers the raw request body; the `shop-domain` header used to identify the tenant is never included in the signed bytes. An attacker who can obtain any single valid `(raw_body, hmac)` pair signed with the app's secret (e.g., by legitimately installing the app on their own shop and capturing one of their own webhook deliveries) can replay that exact body/signature to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. The signature check still passes because it never inspects the header, so the forged tenant identity is delivered to the host application as trusted data.

### Finding Description
The equality that should hold is: `bytes verified by the HMAC == bytes used to determine the shop/tenant`. This is broken here:

- `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  
- `ShopifyAPI::Webhooks::Request#shop` is read straight from the (unsigned) `shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) 
- `ShopifyAPI::Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e. the raw body) and compares it against the `hmac` header: [3](#0-2) 
- `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity that is handed to the app's handler: [4](#0-3) 

Because the same `api_secret_key` is shared across every shop that has the app installed, any tenant that has the app installed (even a free/dev store an attacker controls) can generate a validly-signed `(body, hmac)` pair for themselves and then replay it against the app's public webhook URL with the `shop-domain` header changed to any other merchant's domain. `HmacValidator.validate` will report success because it never checks the header, and `Registry.process` will call the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
This is a cross-tenant confusion vulnerability: the gem's own documentation instructs developers to trust `data.shop` from `WebhookMetadata` as the authoritative tenant identifier once `Registry.process` succeeds (docs/usage/webhooks.md, "This will verify the request did indeed come from Shopify"). Any host application that follows this documented contract (e.g., using `data.shop` to look up which merchant's data/session to update, delete, or act on for topics such as `app/uninstalled`, `orders/create`, `customers/redact`, etc.) can be tricked into applying another merchant's event data/actions against a victim shop's tenant record, or vice versa — a cross-tenant access/write primitive achieved without the app's `client_secret` or any merchant credential, using only a single genuine, self-controlled installation.

### Likelihood Explanation
Any internet user can install a public app on their own (possibly free/dev) store, capture one legitimately delivered webhook `(raw_body, hmac)` pair for their own shop, and replay it to the app's public webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header. No secrets, tokens, or elevated access are required beyond being a normal merchant able to install the target app — a realistically low bar for an "unprivileged internet user."

### Recommendation
Bind the shop identity into the value verified against the HMAC, or otherwise independently authenticate the shop domain before trusting it: e.g., include the `shop-domain` header (and ideally `topic`/`webhook_id`) in `to_signable_string`, or require the host application to cross-check `request.shop` against a shop that is already known/installed (e.g. an existing offline session) before acting on the payload, and update the docs/registry to make clear that `shop` is not itself HMAC-verified.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers any webhook (e.g. `orders/create`) and captures the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent to the app's callback endpoint — this `(body, hmac)` pair is valid because it was signed with the app's real `api_secret_key`.
3. Attacker resends the exact same raw body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` compute the signature from body only [5](#0-4) ; `HmacValidator.validate` succeeds [6](#0-5) .
5. `Registry.process` calls the app's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` [4](#0-3) , even though the payload actually originated from the attacker's own shop.

### Citations

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
