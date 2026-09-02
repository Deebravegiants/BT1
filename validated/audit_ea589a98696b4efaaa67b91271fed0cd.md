### Title
Webhook `shop` identity is not bound by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb` and `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then unconditionally trusts the `shop`, `topic`, `api_version`, and `webhook_id` values taken from unauthenticated HTTP headers when constructing the `WebhookMetadata` handed to the app's handler. Because the `shop` field that identifies which tenant a webhook belongs to is never included in the signed material, any party who can obtain one valid `(body, hmac)` pair for the app (e.g. by installing the app on their own store and receiving a real webhook) can replay that same body/HMAC pair while substituting an arbitrary `X-Shopify-Shop-Domain` header, and the gem will accept it as a legitimately signed webhook "from" the attacker-chosen shop.

### Finding Description
`Utils::HmacValidator.validate` computes and compares an HMAC only over `verifiable_query.to_signable_string`. For webhooks, that value is defined as: [1](#0-0) 

i.e., only the raw JSON body is signed. All identity-bearing fields — including `shop`, `topic`, `api_version`, and `webhook_id` — are read straight from HTTP headers with no HMAC coverage: [2](#0-1) 

`Registry.process` then validates the HMAC and, on success, immediately builds `WebhookMetadata` from those unauthenticated header values and dispatches it to the registered handler: [3](#0-2) 

The binding the gem should enforce is: `shop_that_signed_the_payload == shop_the_handler_is_told_about`. Instead, the gem only enforces `hmac(body) == received_hmac`, which is independent of the `shop` header. Because a Shopify app's client secret (`api_secret_key`) is the same across every shop that installs the app, an unprivileged merchant who installs the app on their own store will receive genuinely-signed webhook bodies with valid HMACs computed under that shared secret. That same `(body, hmac)` pair remains valid when replayed with the `shop-domain` header changed to any other shop, because the header is not part of the signed string. This is precisely the analog of the reported bug class: a field the code *acts on* (here, `shop`, used by the handler to determine which tenant's data the webhook concerns) is not covered by the cryptographic check that is supposed to authenticate the request (the HMAC), so the check answers a question ("is this body correctly signed with the app secret?") different from the one actually relied upon ("did this webhook really come from shop X?").

### Impact Explanation
This breaks the shop/tenant identity binding for webhook processing, allowing a malicious merchant who has legitimately installed the app to forge webhook events attributed to a different shop that also uses the app. Any host application that uses `WebhookMetadata#shop` (the gem's documented, intended field for this purpose) to decide which tenant's records to create/update/delete based on the webhook body is exposed to cross-tenant data injection — satisfying the "cross-tenant access" Critical impact category, since it lets one tenant's authenticated event stream be misattributed to another tenant purely through this gem's verification logic.

### Likelihood Explanation
Exploitation only requires an attacker to be an ordinary, unprivileged user of the app (i.e., install it on their own store, which is often self-serve for public apps) and to capture one webhook `(body, hmac)` pair sent to their own endpoint/logs — no access to `api_secret_key`, no privileged account, and no TLS interception of other tenants' traffic is required. This is fully reachable through the gem's own webhook verification path (`HmacValidator.validate` + `Registry.process`), independent of any host-application misuse.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the signed material verified for webhooks, or otherwise cryptographically bind the `shop` header to the payload before trusting it (e.g., by rejecting/flagging when the header-derived shop cannot be corroborated against the shop that is expected to have generated that specific signed body). Update `Webhooks::Request#to_signable_string` accordingly, or add an explicit post-HMAC check tying `shop` to the verified payload before constructing `WebhookMetadata`.

### Proof of Concept
1. App with `api_secret_key = S` is installed on `attacker-shop.myshopify.com` and on `victim-shop.myshopify.com`.
2. Attacker's own store triggers a webhook; the attacker's server receives `body = B` and header `X-Shopify-Hmac-Sha256 = HMAC(S, B)` together with `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker resends the exact same `body = B` and the same `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC(S, B)` (body-only) and it matches, so `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`.
5. The host application processes attacker-controlled data as if it originated from `victim-shop.myshopify.com`, achieving cross-tenant injection despite a "valid" HMAC. [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
