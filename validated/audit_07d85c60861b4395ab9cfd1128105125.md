### Title
Webhook `shop` identifier is not covered by the HMAC, allowing cross-tenant impersonation of webhook events - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from only the raw request body, while the `shop` (tenant identifier) is read directly from an unauthenticated HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body and then hands the header-derived `shop` value straight to the app's handler as the trusted tenant identity, breaking the intended binding `HMAC(shared_secret, signed_bytes) == HMAC(shared_secret, bytes_used_to_identify_tenant)`.

### Finding Description
`Utils::HmacValidator.validate` verifies a request by comparing `verifiable_query.hmac` against an HMAC computed over `verifiable_query.to_signable_string` using the app's shared `api_secret_key`: [1](#0-0) 

For OAuth callbacks, `AuthQuery#to_signable_string` explicitly includes `shop` as part of the signed bytes, so the shop identity is cryptographically bound to the signature: [2](#0-1) 

For webhooks, however, `Webhooks::Request#to_signable_string` returns only `@raw_body`, while `#shop` is pulled from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never included in the signed bytes: [3](#0-2) [4](#0-3) 

`Registry.process` validates only that the HMAC matches the body, then forwards `request.shop` (the unauthenticated header) to the developer's handler as the tenant identity for that webhook event: [5](#0-4) 

The gem's own documentation confirms that `data.shop` is presented to app code as "The shop domain of the webhook" — i.e., the trusted tenant identifier that apps are expected to act on (e.g., look up sessions, scope data access) without additional verification: [6](#0-5) 

This is structurally the same class of bug as the M-24 report: a value that downstream logic treats as authenticated/bound to a signature (there, `VAULT_FEE()`'s storage offset; here, the `shop` field) is actually *not* covered by the integrity check (there, the wrong `uint8`/offset slice; here, an HTTP header excluded from `to_signable_string`). All Shopify apps share a single `api_secret_key` across every installed shop, so the HMAC on a webhook body only proves "this body was signed by *some* install of this app" — it proves nothing about which shop it came from. An attacker who controls their own shop (i.e., who has legitimately installed the target app on a store they own) receives real, validly-signed webhook deliveries from Shopify for their own shop. Because the `shop` header is not part of the signed bytes, that attacker can replay the exact same `raw_body` + `hmac-sha256` header pair against the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` will still return `true` since it only checks the body/secret pair, and `Registry.process` will invoke the handler with `data.shop` set to the victim's domain.

### Impact Explanation
This crosses the tenant boundary the gem is supposed to enforce: `Registry.process` is documented and relied upon to authenticate "the request did indeed come from Shopify" *for that shop*, but it only authenticates the body content, not the claimed shop. Any app whose webhook handler uses `data.shop` to look up per-tenant session/state (exactly as shown in the gem's own usage example, `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) can be made to process attacker-controlled webhook content under a victim shop's identity — a cross-tenant access vector meeting the Critical bar (cross-tenant access) defined in scope.

### Likelihood Explanation
Likelihood is high for any multi-tenant app built directly on this gem's documented API: the attacker only needs to be a legitimate (even free/trial) installer of the target app on their own store to obtain a validly HMAC-signed webhook body/signature pair, then replay it with a forged `shop` header — no access token, `client_secret`, or privileged account is required.

### Recommendation
Bind the shop identity into the verified bytes for webhooks, mirroring what `AuthQuery` already does for OAuth: either (a) include the `shop` header value in `Webhooks::Request#to_signable_string` so `HmacValidator` rejects any mismatch between the signed body and the claimed shop, or (b) independently verify that the shop claimed in the header is one for which the app currently holds an active session/access token before trusting `data.shop`, rather than exposing the raw header value as an authenticated field in `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook delivery, e.g. for `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — the same `api_secret_key` is shared by every shop installing this app.
2. Attacker POSTs to the app's public webhook endpoint (`ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {"x-shopify-hmac-sha256" => H, "x-shopify-shop-domain" => "victim.myshopify.com", "x-shopify-topic" => "orders/create"}))`).
3. `Utils::HmacValidator.validate` recomputes `HMAC(api_secret_key, B)`, matches `H`, and returns `true` [7](#0-6) .
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(... shop: "victim.myshopify.com", body: parsed body of B ...)` [8](#0-7) , causing the app to act as though attacker-controlled data originated from `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
