The relevant vulnerability class here maps cleanly onto how this gem validates webhook authenticity: the HMAC signs only the raw body, while the tenant identity (`shop`) used downstream is taken from an unsigned header.### Title
Cross-tenant webhook spoofing via unsigned `shop-domain` header not covered by HMAC verification - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` identity used for tenant dispatch from the `X-Shopify-Shop-Domain` HTTP header, while `Utils::HmacValidator` (invoked from `Registry.process`) only verifies the HMAC over the raw request body. The tenant-identifying field is never part of the signed content, so the equality the library implicitly relies on — `shop bound in signature == shop acted upon` — never actually holds.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from a header that is completely outside that signed string: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the HMAC using `verifiable_query.to_signable_string` (i.e. only the body) against the app's single, per-app `Context.api_secret_key`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the tenant-identifying `WebhookMetadata` handed to the app's own handler: [4](#0-3) [5](#0-4) 

Because `Context.api_secret_key` is a single app-level secret shared across every shop that has installed the app, any unprivileged merchant who has installed the app on their own store can trigger a real webhook delivery for their own shop and obtain a body + valid HMAC pair signed with the app's shared secret. Nothing in `Request` or `HmacValidator` binds that valid `(body, hmac)` pair to the `shop-domain` header that accompanied it. An attacker who can influence what header value reaches `Webhooks::Request.new` when replaying that captured request (e.g., because they control delivery to the app's webhook endpoint, a reverse proxy, or otherwise relay the request) can swap the `X-Shopify-Shop-Domain` value to a victim shop's domain while keeping the original valid body/HMAC — the library will still report `HmacValidator.validate(request) == true` and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop.

This is the same class of bug as the referenced report: a value that gates/identifies a privileged operation (`shop` used to select tenant state) is set/derived independently of the value that is actually authenticated (`raw_body` HMAC), letting an attacker who is authorized for one identity (their own shop) make the system act under a different identity.

### Impact Explanation
If a host application (as the library's own docs and `Registry`/`WebhookHandler` pattern instruct) uses `WebhookMetadata#shop` to select which tenant's data to update, delete, or read, an attacker with only unprivileged control of their own shop's install can forge webhook deliveries that are processed as belonging to a different, arbitrary shop. This is a cross-tenant access primitive — the library's own signature-verification API produces a `true` result while binding the wrong tenant identity, which meets the Critical "cross-tenant access" bar defined in scope.

### Likelihood Explanation
Exploitability requires the attacker to control or influence the header value that reaches the app's webhook endpoint on top of a genuinely-signed body/HMAC pair from their own store (e.g. by not using an HTTPS-only relay controlled solely by Shopify, or via any request-forwarding layer that lets the `shop-domain` header be modified after Shopify's HMAC was computed but before this library parses the request). This is a design gap in the library's own verification contract — it never authenticates the field it hands out as the trusted tenant identity — independent of any specific hosting stack, so it is not merely "host misuses a documented API"; the library's `Request`/`HmacValidator` pairing itself is the defect.

### Recommendation
- Extend `HmacValidator`/`Webhooks::Request#to_signable_string` (or add a dedicated check in `Registry.process`) to bind the `shop-domain` (and ideally `topic`, `webhook-id`) header values into the signed material that is verified, not just the raw body.
- Alternatively, document and enforce that `Registry.process` cross-checks `request.shop` against an out-of-band trusted value (e.g., the session/tenant the endpoint is scoped to) before dispatching to `WebhookHandler#handle`, so a mismatch between the signed body and the claimed shop is rejected rather than silently accepted.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; attacker triggers a real event (e.g., product update) causing Shopify to deliver a webhook to the app's endpoint with a valid `X-Shopify-Hmac-Sha256` computed over the JSON body using the app's shared `client_secret`.
2. Attacker captures this `(raw_body, hmac, headers)` triple via a proxy/relay they control in front of the app's webhook endpoint.
3. Attacker resends the identical `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but rewrites `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `Webhooks::Request.new(raw_body:, headers:)` parses `shop` as `"victim-shop.myshopify.com"`.
5. `Utils::HmacValidator.validate(request)` returns `true` because it only checks the (unaltered) body against the (unaltered) HMAC — it never inspects `shop`.
6. `Registry.process(request)` builds `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)` and calls the app's `handler.handle(data:)`, which will act on `victim-shop.myshopify.com`'s tenant data using attacker-supplied `body` content, despite the attacker never having any authorization for that shop.

### Citations

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
